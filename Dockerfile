FROM python:3.11-slim

WORKDIR /app

# Copy your API file
COPY api1.py .

# Install Python dependencies directly (more reliable)
RUN pip install fastapi uvicorn httpx faker user_agent

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "api1:app", "--host", "0.0.0.0", "--port", "8000"]