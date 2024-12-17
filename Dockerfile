FROM python:3.11-slim

WORKDIR /main

# Copy requirements file and validate
COPY requirements.txt .
RUN cat requirements.txt

# Install dependencies with verbose output
RUN pip install --no-cache-dir -r requirements.txt --verbose

# Copy application code
COPY . .

EXPOSE 5000

CMD ["python", "main.py"]
