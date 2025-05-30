from fastapi import FastAPI, Query
import openai
import os
import json
import re
import numpy as np
import faiss

app = FastAPI()

INDEX_PATH = os.path.join(os.path.dirname(__file__), "tnved_combined.index")
DOCS_PATH = os.path.join(os.path.dirname(__file__), "tnved_combined_docs.json")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open(DOCS_PATH, "r", encoding="utf-8") as f:
    documents = json.load(f)

index = faiss.read_index(INDEX_PATH)

def get_embedding(text: str) -> list:
    response = client.embeddings.create(input=[text], model="text-embedding-3-small")
    return response.data[0].embedding

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
    return [documents[i] for i in indices[0]]

@app.get("/search")
def search(query: str = Query(..., description="Текст запроса")):
    matches = search_docs(query)
    context = "\n\n".join([m["text"] for m in matches])

    if context.strip():
        prompt = f"""Ты — эксперт по ТН ВЭД. Вот выдержки из документов:\n\n{context}\n\nНа основе этих данных ответь на вопрос: {query}"""
    else:
        prompt = f"""Ты — эксперт по ТН ВЭД. В базе данных нет официальных пояснений по запросу: {query}. Постарайся объяснить это с точки зрения классификации, если можешь."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Отвечай строго, по сути, как эксперт в области ВЭД. Не уходи в общие фразы."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    result = response.choices[0].message.content
    return {
        "result": result.strip(),
        "matches": matches
    }