FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent.py .

# Set environment variables (will be overridden by docker-compose)
ENV HOSTNAME=endpoint
ENV ENDPOINT_TYPE=workstation
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# Run the agent
CMD ["python", "-u", "agent.py"]
