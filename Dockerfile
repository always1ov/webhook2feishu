FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# 不硬编码端口，通过环境变量传递（关键）
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${APP_PORT:-8080}"]
