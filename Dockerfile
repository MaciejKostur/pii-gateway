FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
COPY src ./src
RUN pip install --no-cache-dir . && python -m spacy download pl_core_news_lg
EXPOSE 8000
CMD ["uvicorn", "pii_gateway.api:app", "--host", "0.0.0.0", "--port", "8000"]
