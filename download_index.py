
import requests
import os

# Получаем ссылки из переменных окружения
INDEX_URL = os.getenv("INDEX_URL")
DOCS_URL = os.getenv("DOCS_URL")

def download(url, filename):
    print(f"⬇️ Скачиваем {filename}...")
    r = requests.get(url)
    r.raise_for_status()
    with open(filename, "wb") as f:
        f.write(r.content)
    print(f"✅ {filename} загружен.")

if __name__ == "__main__":
    download(INDEX_URL, "tnved_combined.index")
    download(DOCS_URL, "tnved_combined_docs.json")
