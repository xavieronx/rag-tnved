
FROM python:3.10

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "python download_index.py && uvicorn main_combined:app --host 0.0.0.0 --port 8000"]
