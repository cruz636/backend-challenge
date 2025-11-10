FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY tests/requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy lambda source code
COPY api_handler /app/api_handler
COPY task_processor /app/task_processor

# Copy test files
COPY tests /app/tests

WORKDIR /app/tests

# Run pytest
CMD ["pytest", "-v"]
