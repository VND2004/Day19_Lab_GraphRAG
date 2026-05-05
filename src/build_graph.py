"""
Build knowledge graph using NodeRAG.
Input: entities.json, relationships.json
Output: graph.json, graph visualization
"""
import json
import os
from typing import Dict, List, Any, Set
import networkx as nx
import matplotlib.pyplot as plt

# For deduplication - alias mapping
ALIASES = {
    "Alphabet Inc.": "Alphabet",
    "Google LLC": "Google",
    "Open AI": "OpenAI",
    "Sam Altmann": "Sam Altman",
    "Microsoft Corp": "Microsoft",
    "Meta Platforms": "Meta",
}

def normalize_entity_name(name: str) -> str:
    """Normalize entity name: trim, lowercase for matching, apply aliases."""
    normalized = " ".join(name.strip().split())
    return ALIASES.get(normalized, normalized)

def load_extracted_data() -> tuple[List[Dict], List[Dict]]:
    """Load entities and relationships from JSON files."""
    with open("outputs/entities.json", "r", encoding="utf-8") as f:
        entities = json.load(f)
    
    with open("outputs/relationships.json", "r", encoding="utf-8") as f:
        relationships = json.load(f)
    
    return entities, relationships

def deduplicate_entities(entities: List[Dict]) -> Dict[str, Dict]:
    """
    Deduplicate entities by normalized name.
    Returns dict: normalized_name -> entity_info
    """
    deduplicated = {}
    for entity in entities:
        normalized = normalize_entity_name(entity["name"])
        if normalized not in deduplicated:
            deduplicated[normalized] = {
                "name": entity["name"],
                "normalized_name": normalized,
                "type": entity.get("type", "Unknown"),
                "chunk_ids": set(),
                "mentions": 1
            }
        else:
            deduplicated[normalized]["mentions"] += 1
            deduplicated[normalized]["chunk_ids"].add(entity.get("chunk_id", ""))
        
        deduplicated[normalized]["chunk_ids"].add(entity.get("chunk_id", ""))
    
    return deduplicated

def build_graph(entities_dict: Dict, relationships: List[Dict]) -> nx.MultiDiGraph:
    """
    Build NetworkX graph with nodes and edges.
    """
    graph = nx.MultiDiGraph()
    
    # Add nodes
    for normalized_name, entity_info in entities_dict.items():
        graph.add_node(normalized_name, 
                      type=entity_info["type"],
                      original_name=entity_info["name"],
                      mentions=entity_info["mentions"])
    
    # Add edges from relationships
    edge_count = 0
    for rel in relationships:
        subject = normalize_entity_name(rel["subject"])
        obj = normalize_entity_name(rel["object"])
        predicate = rel.get("predicate", "RELATED")
        evidence = rel.get("evidence", "")
        
        # Only add edge if both subject and object are in graph
        if subject in graph and obj in graph:
            graph.add_edge(subject, obj,
                          relation=predicate,
                          evidence=evidence,
                          chunk_id=rel.get("chunk_id", ""))
            edge_count += 1
    
    print(f"Graph contains {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
    return graph

def visualize_graph(graph: nx.MultiDiGraph, output_path: str = "outputs/graph.png"):
    """Visualize graph using NetworkX and Matplotlib."""
    plt.figure(figsize=(16, 12))
    
    # Use spring layout for better visualization
    pos = nx.spring_layout(graph, k=2, iterations=50, seed=42)
    
    # Draw nodes by type
    company_nodes = [n for n, attr in graph.nodes(data=True) if attr.get("type") == "Company"]
    person_nodes = [n for n, attr in graph.nodes(data=True) if attr.get("type") == "Person"]
    other_nodes = [n for n in graph.nodes() if n not in company_nodes and n not in person_nodes]
    
    nx.draw_networkx_nodes(graph, pos, nodelist=company_nodes, node_color="skyblue", 
                          node_size=800, label="Company", alpha=0.8)
    nx.draw_networkx_nodes(graph, pos, nodelist=person_nodes, node_color="lightcoral", 
                          node_size=600, label="Person", alpha=0.8)
    nx.draw_networkx_nodes(graph, pos, nodelist=other_nodes, node_color="lightgreen", 
                          node_size=500, label="Other", alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(graph, pos, edge_color="gray", arrows=True, 
                          arrowsize=15, arrowstyle='->', alpha=0.5)
    
    # Draw labels
    nx.draw_networkx_labels(graph, pos, font_size=8)
    
    plt.legend(loc="upper left")
    plt.title("Knowledge Graph: Tech Companies")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"Graph saved to {output_path}")
    plt.close()

def export_graph(graph: nx.MultiDiGraph, output_path: str = "outputs/graph.json"):
    """Export graph as JSON for portability."""
    graph_data = {
        "nodes": [],
        "edges": []
    }
    
    # Export nodes
    for node, attrs in graph.nodes(data=True):
        graph_data["nodes"].append({
            "id": node,
            "type": attrs.get("type", "Unknown"),
            "original_name": attrs.get("original_name", node),
            "mentions": attrs.get("mentions", 0)
        })
    
    # Export edges
    for u, v, key, attrs in graph.edges(keys=True, data=True):
        graph_data["edges"].append({
            "source": u,
            "target": v,
            "relation": attrs.get("relation", "RELATED"),
            "evidence": attrs.get("evidence", ""),
            "chunk_id": attrs.get("chunk_id", "")
        })
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)
    
    print(f"Graph exported to {output_path}")

def main():
    print("Building Knowledge Graph...")
    
    # Load extracted data
    print("Loading extracted entities and relationships...")
    entities, relationships = load_extracted_data()
    
    # Deduplicate entities
    print("Deduplicating entities...")
    entities_dict = deduplicate_entities(entities)
    print(f"After deduplication: {len(entities_dict)} unique entities")
    
    # Build graph
    print("Building NetworkX graph...")
    graph = build_graph(entities_dict, relationships)
    
    # Visualize
    print("Visualizing graph...")
    visualize_graph(graph)
    
    # Export
    print("Exporting graph...")
    export_graph(graph)
    
    # Print statistics
    print(f"\n=== Graph Statistics ===")
    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")
    
    # Count by entity type
    types_count = {}
    for _, attrs in graph.nodes(data=True):
        etype = attrs.get("type", "Unknown")
        types_count[etype] = types_count.get(etype, 0) + 1
    print(f"Entity types: {types_count}")
    
    # Count by relation type
    relations_count = {}
    for u, v, _, attrs in graph.edges(keys=True, data=True):
        rel = attrs.get("relation", "RELATED")
        relations_count[rel] = relations_count.get(rel, 0) + 1
    print(f"Relation types: {relations_count}")
    
    return graph

if __name__ == "__main__":
    main()
