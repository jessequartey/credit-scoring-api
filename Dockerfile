FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set PYTHONPATH so Python can find the app module
ENV PYTHONPATH=/app

# Generate training data and train model during build
RUN python ml/generate_training_data.py && \
    python ml/train_model.py && \
    echo "Model trained successfully" && \
    ls -lh ml/models/

# Create necessary directories
RUN mkdir -p ml/models data config

# Create non-root user and set permissions
RUN useradd -m appuser && \
    chown -R appuser:appuser /app && \
    chmod +x entrypoint.sh

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Use entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
