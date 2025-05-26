FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install PyWebGuard
RUN pip install pywebguard 'pywebguard[fastapi]'

# Copy application code
COPY fastapi_app.py .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"] 