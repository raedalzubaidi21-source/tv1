FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

RUN pip install --no-cache-dir requests

COPY ./main.py /app/main.py
