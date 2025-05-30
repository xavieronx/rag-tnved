
FROM python:3.10

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN python download_index.py

CMD ["uvicorn", "main_combined:app", "--host", "0.0.0.0", "--port", "8000"]
