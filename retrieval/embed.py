import json
import numpy as np
from sentence_transformers import SentenceTransformer


def build_embedding_text(product):
    """
    Combine important fields into one semantic document
    """
    return (
        f"Assessment Name: {product['name']}. "
        f"Description: {product['description']}. "
        f"Test Type: {' '.join(product['test_type'])}. "
        f"Duration: {product['duration']}. "
        f"Remote: {product['remote_support']}."
    )


def generate_embeddings():
    model = SentenceTransformer("all-MiniLM-L6-v2")

    with open("data/processed_catalog.json", "r") as f:
        catalog = json.load(f)

    texts = [build_embedding_text(item) for item in catalog]

    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)

    np.save("data/embeddings.npy", embeddings)

    print("Saved embeddings:", embeddings.shape)


if __name__ == "__main__":
    generate_embeddings()