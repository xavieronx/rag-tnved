
from fastapi import FastAPI, Query
from pathlib import Path
import faiss
import openai
import json
import numpy as np
import re
import os

app = FastAPI()

INDEX_PATH = Path(__file__).parent / "tnved_combined.index"
DOCS_PATH = Path(__file__).parent / "tnved_combined_docs.json"

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    response = client.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding

with open(DOCS_PATH, "r", encoding="utf-8") as f:
    documents = json.load(f)

index = faiss.read_index(str(INDEX_PATH))

def search_docs(query, top_k=10):
    match = re.search(r'\b(\d{4,10})\b', query.replace(" ", ""))
    if match:
        prefix = match.group(1)
        results = [doc for doc in documents if doc["code"].replace(" ", "").startswith(prefix)]
        if results:
            return results

    vector = get_embedding(query)
    vector = np.array(vector).astype("float32").reshape(1, -1)
    scores, indices = index.search(vector, top_k)
    results = [documents[i] for i in indices[0]]
    return results

@app.get("/search")
def search(query: str = Query(..., description="Текст запроса")):
    matches = search_docs(query)
    context = "\n---\n".join([m["text"] for m in matches])

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты эксперт по ТН ВЭД. Отвечай строго по этим данным."},
            {"role": "user", "content": f"Контекст:\n{context}\n\nВопрос: {query}"}
        ],
        temperature=0.2
    )
    answer = response.choices[0].message.content
    return {"result": answer, "matches": matches}
