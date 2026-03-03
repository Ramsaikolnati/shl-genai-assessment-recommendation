from sentence_transformers import SentenceTransformer
from retrieval.vector_store import load_index, load_catalog
import re

model = SentenceTransformer("all-MiniLM-L6-v2")
index = load_index()
catalog = load_catalog()


SKILL_KEYWORDS = [
    "java", "sql", "excel", "python", "selenium",
    "javascript", "marketing", "sales",
    "leadership", "data", "analyst",
    "admin", "bank", "coo"
]

SCREENING_SLUGS = [
    "verify-numerical-ability",
    "verify-verbal-ability-next-generation",
    "shl-verify-interactive-numerical-calculation",
    "shl-verify-interactive-inductive-reasoning",
    "administrative-professional-short-form",
    "professional-7-1",
    "professional-8-0",
    "occupational-personality-questionnaire-opq32r",
    "enterprise-leadership-report"
]

def extract_signals(query):
    q = query.lower()

    skills = [kw for kw in SKILL_KEYWORDS if kw in q]

    intent_tags = []

    if "collaborat" in q or "stakeholder" in q or "cultural" in q:
        intent_tags.append("personality")

    if "cognitive" in q or "numerical" in q or "verbal" in q:
        intent_tags.append("cognitive")

    if "manager" in q or "coo" in q or "lead" in q:
        intent_tags.append("leadership")

    if "graduate" in q or "entry" in q:
        intent_tags.append("entry level")

    duration = None
    if "1 hour" in q or "60" in q:
        duration = "60 minutes"

    return skills, intent_tags, duration


def enrich_query(query):
    skills, tags, duration = extract_signals(query)

    enrichment = " ".join(skills + tags)
    if duration:
        enrichment += " " + duration

    return query + " " + enrichment


def balance_results(results, top_k=10):
    knowledge, personality, others = [], [], []

    for item in results:
        types = item.get("test_type", [])

        if "K" in types:
            knowledge.append(item)
        elif "P" in types:
            personality.append(item)
        else:
            others.append(item)

    balanced = []

    while knowledge and personality and len(balanced) < top_k:
        balanced.append(knowledge.pop(0))
        if len(balanced) < top_k:
            balanced.append(personality.pop(0))

    remaining = knowledge + personality + others

    for item in remaining:
        if len(balanced) >= top_k:
            break
        balanced.append(item)

    return balanced[:top_k]


def recommend(query, top_k=10):
    enriched_query = enrich_query(query)

    query_embedding = model.encode([enriched_query])
    distances, indices = index.search(query_embedding, 100)

    candidates = [catalog[i] for i in indices[0]]

    scored = []
    for i, product in enumerate(candidates):
        embed_score = -distances[0][i]
        screen_score = screening_boost(product)
        final_score = embed_score + screen_score
        scored.append((product, final_score))

    scored.sort(key=lambda x: x[1], reverse=True)

    ranked = [item[0] for item in scored]

    return balance_results(ranked, top_k=top_k)

def screening_boost(product):
    slug = product["url"].split("/")[-2].lower()
    for s in SCREENING_SLUGS:
        if s in slug:
            return 5
    return 0