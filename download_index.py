
import requests
import os

INDEX_URL = os.getenv("https://drive.google.com/file/d/18q-rvIVqJnbybTkkcgi9psb195iP0UU3/view?usp=sharing")
DOCS_URL = os.getenv("https://drive.google.com/file/d/1K8yQKhcdZl_Qx25ObpsoqIVhWk0FNDf3/view?usp=sharing")

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
