FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first
COPY pyproject.toml ./

# Install uv for faster dependency management
RUN pip install uv

# Install dependencies using uv pip for global installation
RUN uv pip install --system fastapi uvicorn redis rq aiohttp pydantic python-dotenv

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Expose port for FastAPI
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]