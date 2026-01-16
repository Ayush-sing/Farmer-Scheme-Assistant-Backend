from app.schemes.index_builder import load_docs, build_index, save_index

docs = load_docs("data/schemes.jsonl")
index, docs, _ = build_index(docs)
save_index(index, docs, "data/schemes.index", "data/schemes_docs.json")
print("Index built successfully")
