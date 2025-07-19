FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv sync

# Copy application code
COPY events_service/ ./events_service/

# Expose port
#EXPOSE 8001

# Set environment variables
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8082
ENV KAFKA_URL=kafka:29092


# Health check

# Run the application
CMD ["uv", "run", "python", "-m", "events_service.main"]
