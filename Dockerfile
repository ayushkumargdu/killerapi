FROM python:3.11-slim

WORKDIR /app

# Copy your API file
COPY api1.py .

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Your try-except will handle Python package installation at runtime
EXPOSE 8080

CMD ["python", "api1.py"]