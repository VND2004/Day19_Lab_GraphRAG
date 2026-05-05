"""
Flat RAG baseline using vector search (ChromaDB) with NVIDIA API for synthesis.
Input: corpus.json
Output: baseline answers for comparison
"""
import json
import os
from typing import List, Dict

import chromadb
from sentence_transformers import SentenceTransformer
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


def load_corpus(filepath: str, max_chunks: int = 0, min_chars: int = 0) -> List[Dict[str, str]]:
    """Load and chunk corpus from JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        corpus_data = json.load(f)

    chunks = []
    for idx, item in enumerate(corpus_data):
        content = item.get("content", "")
        if not content:
            continue

        text_chunks = content.split("\n\n")

        for chunk_idx, text in enumerate(text_chunks):
            clean_text = text.strip()
            if clean_text and len(clean_text) >= min_chars:
                chunks.append(
                    {
                        "chunk_id": f"chunk_{idx:03d}_{chunk_idx:02d}",
                        "text": clean_text,
                        "source": item.get("source", ""),
                        "title": item.get("title", ""),
                    }
                )
                if max_chunks > 0 and len(chunks) >= max_chunks:
                    return chunks

    return chunks


def build_vector_store(chunks: List[Dict[str, str]], collection_name: str = "corpus") -> chromadb.Collection:
    """Build ChromaDB collection with sentence embeddings."""
    client_chroma = chromadb.Client()
    collection = client_chroma.get_or_create_collection(name=collection_name)

    model = SentenceTransformer("all-MiniLM-L6-v2")

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        documents.append(chunk["text"])
        metadatas.append({"source": chunk["source"], "title": chunk["title"]})

    embeddings = model.encode(documents, convert_to_tensor=False).tolist()
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"ChromaDB collection '{collection_name}' created with {len(chunks)} documents")
    return collection


def retrieve_relevant_chunks(collection: chromadb.Collection, question: str, top_k: int = 5) -> List[str]:
    """Retrieve top-k chunks most similar to question."""
    model = SentenceTransformer("all-MiniLM-L6-v2")
    question_embedding = model.encode(question, convert_to_tensor=False).tolist()

    results = collection.query(query_embeddings=[question_embedding], n_results=top_k)
    documents = results["documents"][0] if results["documents"] else []
    return documents


def answer_question_with_flat_rag(
    collection: chromadb.Collection, question: str, client: OpenAI, top_k: int = 5
) -> Dict:
    """Answer question using Flat RAG (vector search + NVIDIA LLM)."""
    print(f"\nQuestion: {question}")

    relevant_chunks = retrieve_relevant_chunks(collection, question, top_k=top_k)
    print(f"Retrieved {len(relevant_chunks)} relevant chunks")

    if not relevant_chunks:
        return {
            "question": question,
            "answer": "No relevant information found in corpus.",
            "supporting_chunks": [],
            "extraction_method": "flat_rag",
        }

    context = "\n".join([f"- {chunk}" for chunk in relevant_chunks])

    prompt = f"""
Answer the question based on the following context from the knowledge base.
If the context doesn't contain enough information, say so explicitly.

Context:
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
        "supporting_chunks": relevant_chunks,
        "extraction_method": "flat_rag",
        "num_chunks": len(relevant_chunks),
    }


def main():
    api_key = os.getenv("NVIDIA_API_KEY")
    api_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1/")

    if not api_key:
        print("Error: NVIDIA_API_KEY not set")
        return

    client = OpenAI(api_key=api_key, base_url=api_url)

    fast_mode = os.getenv("FAST_MODE", "0") == "1"
    default_max_chunks = 350 if fast_mode else 0
    default_min_chars = 80 if fast_mode else 0
    max_chunks = _get_env_int("MAX_CHUNKS", default_max_chunks)
    min_chars = _get_env_int("MIN_CHARS_PER_CHUNK", default_min_chars)
    top_k = _get_env_int("TOP_K_CHUNKS", 3 if fast_mode else 5)

    print("Loading corpus from corpus.json...")
    chunks = load_corpus("data/corpus.json", max_chunks=max_chunks, min_chars=min_chars)
    print(f"Loaded {len(chunks)} chunks")
    if fast_mode:
        print("FAST_MODE is enabled")
    if max_chunks > 0:
        print(f"MAX_CHUNKS={max_chunks}")
    if min_chars > 0:
        print(f"MIN_CHARS_PER_CHUNK={min_chars}")

    print("\nBuilding ChromaDB vector store...")
    collection = build_vector_store(chunks)

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
        result = answer_question_with_flat_rag(collection, q, client, top_k=top_k)
        results.append(result)
        preview = (result["answer"] or "")[:200]
        print(f"Answer: {preview}...")

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/flat_rag_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{len(results)} Flat RAG results saved to outputs/flat_rag_results.json")


if __name__ == "__main__":
    main()
