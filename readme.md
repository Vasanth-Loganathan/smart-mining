# Smart Mining – Edge–Fog–Cloud Monitoring

A locally simulated Edge–Fog–Cloud architecture for real-time mine safety monitoring using Docker, Containernet, and Mininet/SDN.

## Overview

This project simulates a smart mining safety monitoring system where sensor data flows through three computing layers:

**Sensor → Edge → Fog → Cloud**

The system is designed to detect dangerous conditions locally at the Edge while forwarding summarized information through the Fog layer and storing historical data in the Cloud layer.

## Architecture

```text
                    Smart Mining System

     Sensor
   10.0.1.10
       │
       ▼
      s1
       │
       ▼
     Edge
  10.0.1.20
       │
       ▼
      s2
       │
       ▼
      Fog
  10.0.2.30
       │
       ▼
      s3
       │
       ▼
     Cloud
  10.0.3.40

Components
Sensor – Generates simulated mining environment readings.
Edge – Performs local anomaly detection and generates immediate safety alerts.
Fog – Provides mine-level coordination and buffers data when Cloud connectivity is unavailable.
Cloud – Stores historical sensor readings and alerts using SQLite.
SDN Network – Connects the different layers using a virtual network created with Mininet/Containernet.
Edge Cache/CDN – Maintains frequently accessed safety information at the Edge.
Sensor Data

The simulated sensors generate:

Gas concentration
Temperature
Vibration
Humidity

Example reading:

{
  "gas_ppm": 25.51,
  "temperature_c": 35.5,
  "vibration": 1.83,
  "humidity_percent": 66.2
}
Edge Processing

The Edge layer checks sensor readings locally for dangerous conditions.

Examples:

High gas level
High temperature
High vibration

When a dangerous condition is detected, the Edge immediately generates an alert before forwarding information to the Fog layer.

Fog Processing

The Fog layer receives summarized information from the Edge.

It:

Coordinates mine-level information
Tracks received readings
Tracks alerts
Maintains a buffer for Cloud connectivity failures
Forwards data to the Cloud when connectivity is available
Cloud Storage

The Cloud layer stores historical readings in an SQLite database.

Stored information includes:

Timestamp
Gas level
Temperature
Vibration
Humidity
Danger status
Alerts
SDN / Containernet

The virtual network is created using Containernet and Mininet.

Topology:

Sensor -- s1 -- Edge -- s2 -- Fog -- s3 -- Cloud

IP addresses:

Component	IP Address
Sensor	10.0.1.10
Edge	10.0.1.20
Edge-Fog interface	10.0.2.20
Fog	10.0.2.30
Fog-Cloud interface	10.0.3.30
Cloud	10.0.3.40
Requirements
Linux
Docker
Python 3
Containernet
Mininet
Flask
Python Requests
Running the Project

Start the Containernet environment:

sudo docker run --name containernet -it --rm \
  --privileged \
  --pid=host \
  --net=host \
  -v /var/run/docker.sock:/var/run/docker.sock \
  # Smart Mining — Edge–Fog–Cloud Monitoring

  A local simulation of an Edge–Fog–Cloud architecture for real-time mine safety monitoring using Docker and Containernet/Mininet.

  ## Overview

  Sensor data flows through three layers: Sensor → Edge → Fog → Cloud. The Edge performs local anomaly detection and immediate alerting, the Fog coordinates mine-level aggregation and buffering, and the Cloud stores historical data.

  ## Architecture

  ```
  Smart Mining System

  Sensor (10.0.1.10)
     |
    s1
     |
   Edge (10.0.1.20)
     |
    s2
     |
   Fog (10.0.2.30)
     |
    s3
     |
   Cloud (10.0.3.40)
  ```

  ### Components
  - **Sensor** — Generates simulated mining environment readings (gas, temperature, vibration, humidity).
  - **Edge** — Performs local anomaly detection and creates immediate safety alerts.
  - **Fog** — Aggregates and buffers summaries from multiple Edges; forwards to Cloud when available.
  - **Cloud** — Stores historical readings and alerts (SQLite by default).
  - **SDN Network** — Virtual network implemented with Containernet/Mininet connecting the components.

  ## Sensor data

  Simulated sensor readings include:
  - Gas concentration
  - Temperature
  - Vibration
  - Humidity

  Example JSON reading:

  ```json
  {
    "gas_ppm": 25.51,
    "temperature_c": 35.5,
    "vibration": 1.83,
    "humidity_percent": 66.2
  }
  ```

  ## Edge processing

  The Edge checks incoming readings for hazardous conditions (for example: high gas, high temperature, or excessive vibration). When a dangerous condition is detected, the Edge emits an alert immediately and also forwards summarized data to the Fog.

  ## Fog processing

  The Fog layer receives summarized data from Edges, tracks readings and alerts, and buffers data while Cloud connectivity is unavailable. Buffered data is forwarded to the Cloud when connectivity is restored.

  ## Cloud storage

  The Cloud component stores historical readings and alerts in an SQLite database. Typical stored fields include timestamp, gas level, temperature, vibration, humidity, danger status, and alert details.

  ## SDN / Containernet

  The network topology is created using Containernet/Mininet. Example topology:

  Sensor -- s1 -- Edge -- s2 -- Fog -- s3 -- Cloud

  Example IP addresses (adjustable in `smart_mining_sdn.py`):

  | Component | IP Address |
  |---|---:|
  | Sensor | 10.0.1.10 |
  | Edge | 10.0.1.20 |
  | Edge–Fog interface | 10.0.2.20 |
  | Fog | 10.0.2.30 |
  | Fog–Cloud interface | 10.0.3.30 |
  | Cloud | 10.0.3.40 |

  ## Requirements
  - Linux
  - Docker
  - Python 3.8+
  - Containernet (for SDN simulation)
  - Mininet
  - Python packages: `flask`, `requests`

  ## Running the project (example)

  Start a Containernet runtime (example using the public image):

  ```bash
  sudo docker run --name containernet -it --rm \
    --privileged \
    --pid=host \
    --net=host \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v "$PWD":/smart-mining \
    containernet/containernet /bin/bash
  ```

  Inside the Containernet container run:

  ```bash
  python3 /smart-mining/smart_mining_sdn.py
  ```

  This will create the virtual network and start the Sensor, Edge, Fog, and Cloud services.

  ## Monitoring

  Run the terminal monitor locally (or inside the Containernet runtime):

  ```bash
  python3 demo_monitor.py
  ```

  The monitor shows system status, latest sensor readings, Edge decisions, Fog status, Cloud storage stats, and recent alerts.

  ## Cloud failure demonstration

  To simulate Cloud outage, stop the Cloud container (example name may vary):

  ```bash
  sudo docker stop mn.cloud
  ```

  During an outage the Edge and Fog continue operating and Fog will buffer data intended for the Cloud until connectivity is restored.

  ## Project structure

  ```
  smart-mining/
  ├── edge/
  │   ├── app.py
  │   └── Dockerfile
  ├── fog/
  │   ├── app.py
  │   └── Dockerfile
  ├── cloud/
  │   ├── app.py
  │   └── Dockerfile
  ├── sensor/
  │   ├── sensor_simulator.py
     └── Dockerfile
  ├── smart_mining_sdn.py
  ├── demo_monitor.py
  └── readme.md
  ```

  ## Notes
  - Adjust IP addresses and container names in `smart_mining_sdn.py` as needed for your environment.
  - If you want, I can add a `requirements.txt` and example Docker Compose to simplify running the components.
