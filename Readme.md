# SHL Assessment Recommendation Engine

## Problem Overview

The goal of this project is to build an intelligent recommendation engine that suggests relevant SHL assessments based on a given job description or hiring query.

Given:
- A product catalogue of SHL assessments
- A set of training queries with expected assessment URLs
- A test set of unseen queries

The objective is to retrieve the top 10 most relevant assessments for each query.

---

## System Architecture

The system consists of the following components:

### 1. Data Collection (Web Scraping)

The SHL Product Catalogue was scraped dynamically using Selenium.

Extracted fields:
- Assessment Name
- URL
- Description
- Test Type (K, P, A, etc.)
- Duration
- Remote Support flag

The final processed catalogue contains 437 assessments.

---

### 2. Embedding & Vector Indexing

We used:

- `sentence-transformers/all-MiniLM-L6-v2`
- FAISS for vector similarity search

Each assessment was converted into dense embeddings using:


Embeddings are stored and indexed using FAISS for efficient retrieval.

---

### 3. Retrieval Strategy

Initial Approach:
- Dense retrieval using embeddings
- Returned low recall (~0.01 initially)

Improved Strategy:
- Query enrichment (skill extraction, intent tagging)
- Screening-test boosting (dataset bias alignment)
- Balanced Knowledge (K) and Personality (P) mix
- Final reranking combining:
  - Embedding similarity
  - Screening boost signal

This improved performance significantly.

---

## Evaluation

Evaluation Metric:
- Recall@10

URL normalization is performed using slug matching to handle:
- Trailing slashes
- /solutions vs /products paths

Performance progression:

| Version | Mean Recall@10 |
|----------|----------------|
| Dense only | ~0.01 |
| Hybrid reranking | ~0.14 |
| Enriched + Screening Boost | **~0.30** |

Final Mean Recall@10 ≈ **0.30**

---

## Test Submission

Predictions for the Test-Set were generated using:

python generate_submission.py


Output file:

submission.csv

Format:

Query,Assessment_url
Query1,URL1
Query1,URL2
...


Each query has 10 recommended assessments.

---

## Project Structure

shl-recommender/
│
├── scraper/
├── retrieval/
├── evaluation/
├── data/
│ ├── raw_catalog.json
│ ├── processed_catalog.json
│ └── Gen_AI Dataset.xlsx
│
├── generate_submission.py
├── submission.csv
├── requirements.txt
└── README.md


---

## How To Run

### 1. Install Dependencies

pip install -r requirements.txt


### 2. Evaluate on Train Set


python -m evaluation.evaluate


### 3. Generate Test Submission


python generate_submission.py


---

## Design Decisions & Tradeoffs

### Why Dense Retrieval Alone Was Insufficient

Long job descriptions introduce noise. MiniLM embeddings struggled with domain bias present in training labels.

### Why Screening Boost Was Required

The training dataset strongly favored general screening assessments (Verify Numerical, OPQ, Professional Short Forms).

To align model behavior with dataset patterns, a screening boost was introduced.

### Why URL Slug Normalization Was Necessary

URLs differed between:


Exact string match caused false negatives during evaluation. Slug-based matching fixed this.

---

## Possible Improvements

- Fine-tune embedding model on SHL query–assessment pairs
- Introduce learning-to-rank model
- Add BM25 + dense fusion with weighted optimization
- Deploy via FastAPI + UI interface

---

## Conclusion

This system demonstrates:

- End-to-end data scraping
- Embedding-based semantic retrieval
- Hybrid ranking design
- Bias alignment with dataset patterns
- Structured evaluation using Recall@10

The final system provides meaningful recommendations with measurable improvement over baseline approaches.