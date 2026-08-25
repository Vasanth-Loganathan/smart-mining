import json
import random
import time
from datetime import datetime

import requests


# This will later become the Edge container's
# SDN-reachable address.
EDGE_URL = "http://10.0.1.20:5000/sensor"

def generate_reading():
    """
    Generate raw sensor measurements.

    The sensor does NOT classify anomalies.
    It only measures physical values.
    """

    gas = round(random.uniform(10, 40), 2)
    temperature = round(random.uniform(25, 40), 2)
    vibration = round(random.uniform(0.1, 2.0), 2)
    humidity = round(random.uniform(40, 80), 2)

    # Occasionally generate abnormal physical measurements.
    # The sensor still does not know they are abnormal.
    if random.random() < 0.10:

        abnormal_value = random.choice([
            "gas",
            "temperature",
            "vibration"
        ])

        if abnormal_value == "gas":
            gas = round(random.uniform(70, 100), 2)

        elif abnormal_value == "temperature":
            temperature = round(random.uniform(65, 90), 2)

        elif abnormal_value == "vibration":
            vibration = round(random.uniform(6, 10), 2)

    return {
        "timestamp": datetime.now().isoformat(),
        "gas_ppm": gas,
        "temperature_c": temperature,
        "vibration": vibration,
        "humidity_percent": humidity
    }


def send_to_edge(reading):

    try:
        response = requests.post(
            EDGE_URL,
            json=reading,
            timeout=3
        )

        return response.json()

    except requests.exceptions.RequestException as error:

        return {
            "status": "edge_unreachable",
            "error": str(error)
        }


def main():

    print("====================================")
    print(" Smart Mining Sensor Simulator")
    print("====================================")
    print(f"Target Edge: {EDGE_URL}")
    print()

    while True:

        reading = generate_reading()

        print(
            "SENSOR:",
            json.dumps(reading),
            flush=True
        )

        edge_response = send_to_edge(reading)

        print(
            "EDGE:",
            json.dumps(edge_response),
            flush=True
        )

        print("-" * 70, flush=True)

        time.sleep(2)


if __name__ == "__main__":
    main()
