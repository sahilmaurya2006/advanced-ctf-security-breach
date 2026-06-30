FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY web_server/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY web_server/ .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
