FROM python:3.9-slim

# Install netcat (nc) so the wait script can use 'nc -z'
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the instance directory exists and is writable
RUN mkdir -p instance
RUN chmod a+rw instance

# Copy the rest of your application code
COPY . .

# Set environment variables (optional, overridden by docker-compose)
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

# Copy your startup script (the one that waits for DB, applies migrations, etc.)
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

EXPOSE 8000

# Finally, run your startup script
CMD ["/startup.sh"]
