FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any are needed (e.g. gcc, curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies first to leverage caching
COPY backend_python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend python code and AI bot logic
COPY backend_python/ ./backend_python/
COPY ai_bot/ ./ai_bot/

# Set Python path to ensure imports resolve from root
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "backend_python.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
