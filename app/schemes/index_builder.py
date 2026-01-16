import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def load_docs(jsonl_path: str):
    docs = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            docs.append(json.loads(line))
    return docs

def build_index(docs):
    model = SentenceTransformer(MODEL_NAME)

    texts = [
        f"{d['scheme_name']} | {d.get('summary','')} | {d.get('eligibility','')} | {d.get('benefits','')} | tags: {', '.join(d.get('tags',[]))}"
        for d in docs
    ]

    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    embeddings = embeddings.astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    return index, docs, model

def save_index(index, docs, index_path: str, docs_path: str):
    faiss.write_index(index, index_path)
    with open(docs_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
