FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y iproute2 iputils-ping && \
    rm -rf /var/lib/apt/lists/*

COPY sensor_simulator.py .

RUN pip install --no-cache-dir requests

CMD ["python", "sensor_simulator.py"]
