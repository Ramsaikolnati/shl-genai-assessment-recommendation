import pandas as pd
from retrieval.recommender import recommend


def extract_slug(url):
    url = url.strip()
    if url.endswith("/"):
        url = url[:-1]
    return url


def generate_submission(input_file, output_file):
    # Read Test-Set sheet
    df = pd.read_excel(input_file, sheet_name="Test-Set")

    rows = []

    for _, row in df.iterrows():
        query = row["Query"]

        predictions = recommend(query, top_k=10)

        for p in predictions:
            rows.append({
                "Query": query,
                "Assessment_url": extract_slug(p["url"])
            })

    submission_df = pd.DataFrame(rows)

    submission_df.to_csv(output_file, index=False)

    print("Submission file generated:", output_file)


if __name__ == "__main__":
    generate_submission(
        "data/Gen_AI Dataset.xlsx",
        "submission.csv"
    )