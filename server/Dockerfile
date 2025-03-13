# Build stage
FROM python:3.12-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libfreetype6-dev \
    libxml2-dev \
    libxslt-dev \
    zlib1g-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
# Install packages into /install
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
# Copy installed packages from builder
COPY --from=builder /install /install
# Copy application code
COPY . .

# Add /install/bin to PATH so that the installed executables are available
ENV PATH=/install/bin:$PATH
# Add the custom site-packages directory to PYTHONPATH so that Python finds the modules
ENV PYTHONPATH=/install/lib/python3.12/site-packages:$PYTHONPATH
ENV FLASK_ENV=production
ENV PORT=${PORT:-5000}

EXPOSE $PORT
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 backend:app"]
