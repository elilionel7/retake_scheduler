# Dockerfile

FROM python:3.9-slim

WORKDIR /app


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

COPY startup.sh /startup.sh
RUN chmod +x /startup.sh
# Expose port 5000 (Flask default)
EXPOSE 8000

# Run migrations and start the Flask app
CMD ["/startup.sh"]