"""
Query knowledge graph using BFS (1-hop and 2-hop traversal) with NVIDIA API.
Input: graph.json
Output: query results with supporting triples
"""
import json
import os
from typing import List, Dict, Set, Tuple
from collections import deque

import networkx as nx
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file
load_dotenv()


def _get_env_int(name: str, default: int) -> int:
    """Read integer environment variable with safe fallback."""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def load_graph() -> nx.MultiDiGraph:
    """Load graph from JSON export."""
    with open("outputs/graph.json", "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    graph = nx.MultiDiGraph()

    for node in graph_data["nodes"]:
        graph.add_node(
            node["id"],
            type=node.get("type", "Unknown"),
            original_name=node.get("original_name", node["id"]),
        )

    for edge in graph_data["edges"]:
        graph.add_edge(
            edge["source"],
            edge["target"],
            relation=edge.get("relation", "RELATED"),
            evidence=edge.get("evidence", ""),
            chunk_id=edge.get("chunk_id", ""),
        )

    return graph


def extract_question_entities(question: str, client: OpenAI) -> List[str]:
    """Use LLM to extract key entities from question via NVIDIA API."""
    prompt = f"""
Extract the main entities (companies, people, products) mentioned in this question.
Return as JSON array of strings: ["entity1", "entity2", ...]

Question: {question}

Return only valid JSON, no explanation.
"""

    try:
        response = client.chat.completions.create(
            model=os.getenv("AGENT_MODEL", "openai/gpt-oss-20b"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=150,
        )
        content = response.choices[0].message.content
        if not content:
            return []
        entities = json.loads(content)
        return entities if isinstance(entities, list) else []
    except Exception:
        return []


def bfs_neighbors(graph: nx.MultiDiGraph, start_node: str, max_hops: int = 2) -> Dict[int, Set[str]]:
    """BFS to find neighbors within max_hops."""
    neighbors_by_hop = {0: {start_node}}
    visited = {start_node}
    queue = deque([(start_node, 0)])

    while queue:
        node, hops = queue.popleft()

        if hops < max_hops:
            for neighbor in graph.successors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    neighbors_by_hop.setdefault(hops + 1, set()).add(neighbor)
                    queue.append((neighbor, hops + 1))

            for neighbor in graph.predecessors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    neighbors_by_hop.setdefault(hops + 1, set()).add(neighbor)
                    queue.append((neighbor, hops + 1))

    return neighbors_by_hop


def collect_triples_for_nodes(graph: nx.MultiDiGraph, nodes: Set[str]) -> List[Tuple[str, str, str, str]]:
    """Collect all triples between given nodes."""
    triples = []
    for u in nodes:
        for v in nodes:
            if graph.has_edge(u, v):
                for _, attrs in graph[u][v].items():
                    triples.append(
                        (
                            u,
                            attrs.get("relation", "RELATED"),
                            v,
                            attrs.get("evidence", ""),
                        )
                    )
    return triples


def textualize_triples(triples: List[Tuple[str, str, str, str]]) -> str:
    """Convert triples to readable text for LLM context."""
    if not triples:
        return "No related information found."

    lines = []
    for subject, predicate, obj, evidence in triples:
        readable_pred = predicate.lower().replace("_", " ")
        line = f"- {subject} {readable_pred} {obj}."
        if evidence:
            line += f" (Evidence: {evidence[:100]})"
        lines.append(line)

    return "\n".join(lines)


def answer_question_with_graph(
    graph: nx.MultiDiGraph,
    question: str,
    client: OpenAI,
    max_hops: int,
) -> Dict:
    """Answer question using graph-based retrieval via NVIDIA API."""
    print(f"\nQuestion: {question}")

    extracted_entities = extract_question_entities(question, client)
    print(f"Extracted entities: {extracted_entities}")

    matching_nodes = set()
    for entity in extracted_entities:
        entity_lower = entity.lower()
        for node in graph.nodes():
            node_lower = node.lower()
            if entity_lower in node_lower or node_lower in entity_lower:
                matching_nodes.add(node)
                break

    if not matching_nodes:
        print("No matching entities found in graph")
        return {
            "question": question,
            "answer": "No matching entities found in knowledge graph.",
            "supporting_triples": [],
            "extraction_method": "graph",
        }

    print(f"Matching nodes: {matching_nodes}")

    all_relevant_nodes = set(matching_nodes)
    for node in matching_nodes:
        neighbors = bfs_neighbors(graph, node, max_hops=max_hops)
        for hop_nodes in neighbors.values():
            all_relevant_nodes.update(hop_nodes)

    print(f"Collected {len(all_relevant_nodes)} nodes within {max_hops}-hop distance")

    triples = collect_triples_for_nodes(graph, all_relevant_nodes)
    print(f"Collected {len(triples)} supporting triples")

    context = textualize_triples(triples)

    prompt = f"""
Answer the question based on the following knowledge graph context.
If the context doesn't contain enough information, say so explicitly.

Context (Knowledge Graph):
{context}

Question: {question}

Provide a clear, factual answer based only on the context provided.
"""

    try:
        response = client.chat.completions.create(
            model=os.getenv("AGENT_MODEL", "openai/gpt-oss-20b"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=400,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        print(f"Error calling API: {e}")
        answer = "Error processing question."

    return {
        "question": question,
        "answer": answer,
        "supporting_triples": [(s, p, o) for s, p, o, _ in triples],
        "extraction_method": "graph",
        "num_triples": len(triples),
    }


def main():
    api_key = os.getenv("NVIDIA_API_KEY")
    api_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1/")

    if not api_key:
        print("Error: NVIDIA_API_KEY not set")
        return

    client = OpenAI(api_key=api_key, base_url=api_url)

    fast_mode = os.getenv("FAST_MODE", "0") == "1"
    max_hops = _get_env_int("MAX_HOPS", 1 if fast_mode else 2)

    print("Loading knowledge graph...")
    graph = load_graph()
    print(f"Graph loaded: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    if fast_mode:
        print("FAST_MODE is enabled")
    print(f"MAX_HOPS={max_hops}")

    test_questions = [
        "Who founded OpenAI?",
        "What is the relationship between Microsoft and OpenAI?",
        "What products did OpenAI develop?",
        "Who owns Google?",
        "What technology does NVIDIA develop?",
    ]
    question_limit = _get_env_int("QUESTION_LIMIT", 3 if fast_mode else len(test_questions))
    test_questions = test_questions[: max(1, question_limit)]

    results = []
    for q in test_questions:
        result = answer_question_with_graph(graph, q, client, max_hops=max_hops)
        results.append(result)
        preview = (result["answer"] or "")[:200]
        print(f"Answer: {preview}...")

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/query_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{len(results)} query results saved to outputs/query_results.json")


if __name__ == "__main__":
    main()
