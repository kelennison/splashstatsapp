# Build stage
FROM python:3.12-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --user --no-cache-dir --no-warn-script-location -r requirements.txt

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV FLASK_ENV=production
ENV PORT=${PORT:-5000}

EXPOSE $PORT
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --workers 4 backend:app"]