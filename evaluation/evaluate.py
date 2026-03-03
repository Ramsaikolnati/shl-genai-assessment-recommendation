import pandas as pd
from retrieval.recommender import recommend


def extract_slug(url):
    url = url.lower().strip()

    # remove trailing slash
    if url.endswith("/"):
        url = url[:-1]

    # take last part
    return url.split("/")[-1]


def recall_at_k(predicted_urls, true_urls, k=10):
    predicted_top_k = predicted_urls[:k]

    pred_slugs = [extract_slug(u) for u in predicted_top_k]
    true_slugs = [extract_slug(u) for u in true_urls]

    hits = len(set(pred_slugs) & set(true_slugs))

    return hits / len(true_slugs) if true_slugs else 0


def evaluate(file_path):
    # Read TRAIN sheet explicitly
    df = pd.read_excel(file_path, sheet_name="Train-Set")

    # Group URLs per query
    grouped = df.groupby("Query")["Assessment_url"].apply(list).reset_index()

    scores = []

    for _, row in grouped.iterrows():
        query = row["Query"]
        true_urls = row["Assessment_url"]

        predictions = recommend(query, top_k=10)
        predicted_urls = [p["url"] for p in predictions]

        score = recall_at_k(predicted_urls, true_urls, k=10)
        scores.append(score)

        print("\nQuery:")
        print(query[:100])
        print("Recall@10:", score)
        print("-" * 60)
        
        print("True URLs:")
        print(true_urls[:3])

        print("Predicted URLs:")
        print(predicted_urls[:3])

    mean_recall = sum(scores) / len(scores)
    print("\nFINAL Mean Recall@10:", mean_recall)

    return mean_recall


if __name__ == "__main__":
    evaluate("data/Gen_AI Dataset.xlsx")