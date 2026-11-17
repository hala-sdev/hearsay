FROM python:3.11-slim


ENV PYTHONUNBUFFERED=1 \
    NLTK_DATA=/app/nltk_data \
    FASTEMBED_CACHE_PATH=/app/models


WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader -d /app/nltk_data punkt_tab
# must match dense_embedding_model and sparse_embedding_model in hearsay/config
RUN python -c "from fastembed import TextEmbedding, SparseTextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5'); SparseTextEmbedding('Qdrant/bm25')"

COPY . .

CMD ["sh", "-c", "uvicorn hearsay.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]