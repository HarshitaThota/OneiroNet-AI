# Minimal, reproducible container
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps (use ROOT requirements.txt)
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy app code
COPY backend /app/backend

EXPOSE 8000
ENV OPENAI_API_KEY=""
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
