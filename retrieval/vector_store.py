import faiss
import numpy as np
import json


def load_index():
    # Load embeddings
    embeddings = np.load("data/embeddings.npy")

    dimension = embeddings.shape[1]

    # Create FAISS index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return index


def load_catalog():
    # Load product metadata
    with open("data/processed_catalog.json", "r", encoding="utf-8") as f:
        catalog = json.load(f)

    return catalog