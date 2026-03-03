import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="SHL Assessment Recommendation API")

model_loaded = False
recommend_fn = None


def load_model():
    global model_loaded, recommend_fn
    if not model_loaded:
        from retrieval.recommender import recommend
        recommend_fn = recommend
        model_loaded = True


class QueryRequest(BaseModel):
    query: str


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>SHL Assessment Recommendation Tool</title>
    </head>
    <body>
        <h2>SHL Assessment Recommendation Tool</h2>
        <form action="/recommend_form" method="post">
            <textarea name="query" rows="8" cols="80"
            placeholder="Enter job description or hiring query"></textarea><br><br>
            <button type="submit">Recommend</button>
        </form>
    </body>
    </html>
    """


@app.post("/recommend_form", response_class=HTMLResponse)
def recommend_form(query: str = Form(...)):
    load_model()
    results = recommend_fn(query, top_k=10)

    html = "<h2>Recommendations</h2><ul>"

    for r in results:
        html += f"<li><strong>{r['name']}</strong><br>"
        html += f"<a href='{r['url']}' target='_blank'>{r['url']}</a><br><br></li>"

    html += "</ul><br><a href='/'>Back</a>"
    return html


@app.post("/recommend")
def get_recommendations(request: QueryRequest):
    load_model()
    results = recommend_fn(request.query, top_k=10)
    return {
        "query": request.query,
        "recommendations": results
    }


@app.get("/recommend")
def recommend_get(query: str):
    load_model()
    results = recommend_fn(query, top_k=10)
    return {
        "query": query,
        "recommendations": results
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)