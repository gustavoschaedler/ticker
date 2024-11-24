FROM python:3.12-alpine

# Add non-root user for better security
RUN adduser -D appuser

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY app/ .

# Switch to non-root user
USER appuser

CMD ["python", "server.py"]
