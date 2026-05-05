"""
Extract entities and relationships from corpus using NVIDIA API.
Input: data/corpus.json
Output: entities.json, relationships.json
"""
import json
import os
import re
import time
from typing import List, Dict, Any
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
    """Load corpus from JSON file and prepare chunks."""
    with open(filepath, 'r', encoding='utf-8') as f:
        corpus_data = json.load(f)
    
    chunks = []
    for idx, item in enumerate(corpus_data):
        # Use content field from corpus.json
        content = item.get("content", "")
        if not content:
            continue
        
        # Split content into paragraphs/sentences
        text_chunks = content.split('\n\n')  # Split by double newlines
        
        for chunk_idx, text in enumerate(text_chunks):
            clean_text = text.strip()
            if clean_text and len(clean_text) >= min_chars:
                chunks.append({
                    "chunk_id": f"chunk_{idx:03d}_{chunk_idx:02d}",
                    "text": clean_text,
                    "source": item.get("source", "unknown"),
                    "title": item.get("title", ""),
                    "url": item.get("url", "")
                })
                if max_chunks > 0 and len(chunks) >= max_chunks:
                    return chunks
    
    return chunks


def _extract_json_object(raw_text: str) -> Dict[str, Any]:
    """Parse first JSON object from model output, handling markdown code fences."""
    if not raw_text:
        raise ValueError("Empty model response")

    text = raw_text.strip()

    # Handle fenced code block like ```json ... ```
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, flags=re.DOTALL)
    if fence_match:
        return json.loads(fence_match.group(1))

    # Fallback: find first JSON object boundaries
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start:end + 1])

    return json.loads(text)

def extract_entities_and_relations(chunk: Dict[str, str], client: OpenAI, api_key: str, api_url: str) -> Dict[str, Any]:
    """
    Use LLM to extract entities and relations from a chunk.
    Uses NVIDIA API via OpenAI-compatible interface.
    """
    prompt = f"""
Extract entities (people, companies, products, locations) and relationships from this text.
Return a JSON object with this structure:
{{
  "entities": [
    {{"name": "...", "type": "Company|Person|Product|Organization|Location|Time"}}
  ],
  "relationships": [
    {{
      "subject": "...",
      "predicate": "FOUNDED_BY|FOUNDED_IN|CEO_OF|OWNED_BY|SUBSIDIARY_OF|INVESTED_IN|PARTNERED_WITH|DEVELOPED|USES|LOCATED_IN",
      "object": "...",
      "evidence": "..."
    }}
  ]
}}

Text: {chunk['text'][:1000]}

Only extract relationships that are explicitly stated in the text. Return valid JSON only, no explanation.
"""
    
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": "Return only a valid JSON object. No markdown, no explanation."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=1000
            )

            message = response.choices[0].message
            content = message.content
            if content is None:
                raise ValueError("Model returned empty content")

            result = _extract_json_object(content)
            result["chunk_id"] = chunk["chunk_id"]
            result["source"] = chunk["source"]
            return result
        except (json.JSONDecodeError, ValueError) as e:
            if attempt == 0:
                time.sleep(0.2)
                continue
            print(f"Failed to parse response for chunk {chunk['chunk_id']}: {e}")
            return {"entities": [], "relationships": [], "chunk_id": chunk["chunk_id"], "source": chunk["source"]}
        except Exception as e:
            print(f"Error processing chunk {chunk['chunk_id']}: {e}")
            return {"entities": [], "relationships": [], "chunk_id": chunk["chunk_id"], "source": chunk["source"]}

def main():
    # Get API credentials from environment
    api_key = os.getenv("NVIDIA_API_KEY")
    api_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1/")
    
    if not api_key:
        print("Error: NVIDIA_API_KEY not set in environment")
        return
    
    # Initialize NVIDIA API client (OpenAI-compatible)
    client = OpenAI(
        api_key=api_key,
        base_url=api_url
    )

    fast_mode = os.getenv("FAST_MODE", "0") == "1"
    default_max_chunks = 250 if fast_mode else 0
    default_min_chars = 80 if fast_mode else 0
    max_chunks = _get_env_int("MAX_CHUNKS", default_max_chunks)
    min_chars = _get_env_int("MIN_CHARS_PER_CHUNK", default_min_chars)
    
    # Load corpus
    print("Loading corpus from corpus.json...")
    chunks = load_corpus("data/corpus.json", max_chunks=max_chunks, min_chars=min_chars)
    print(f"Loaded {len(chunks)} chunks")
    if fast_mode:
        print("FAST_MODE is enabled")
    if max_chunks > 0:
        print(f"MAX_CHUNKS={max_chunks}")
    if min_chars > 0:
        print(f"MIN_CHARS_PER_CHUNK={min_chars}")
    
    # Extract entities and relations
    print("Extracting entities and relations...")
    all_entities = []
    all_relationships = []
    
    for i, chunk in enumerate(chunks):
        if i % 5 == 0:
            print(f"Processing chunk {i+1}/{len(chunks)}...")
        
        result = extract_entities_and_relations(chunk, client, api_key, api_url)
        
        # Add source info to entities
        for entity in result.get("entities", []):
            entity["chunk_id"] = chunk["chunk_id"]
            entity["source"] = chunk["source"]
            all_entities.append(entity)
        
        # Add source info to relationships
        for rel in result.get("relationships", []):
            rel["chunk_id"] = chunk["chunk_id"]
            rel["source"] = chunk["source"]
            all_relationships.append(rel)
    
    # Save results
    os.makedirs("outputs", exist_ok=True)
    
    with open("outputs/entities.json", "w", encoding="utf-8") as f:
        json.dump(all_entities, f, indent=2, ensure_ascii=False)
    
    with open("outputs/relationships.json", "w", encoding="utf-8") as f:
        json.dump(all_relationships, f, indent=2, ensure_ascii=False)
    
    print(f"\nExtracted {len(all_entities)} entities and {len(all_relationships)} relationships")
    print("Results saved to outputs/entities.json and outputs/relationships.json")

if __name__ == "__main__":
    main()
