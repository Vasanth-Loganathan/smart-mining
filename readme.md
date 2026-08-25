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
```

### Components
- **Sensor** – Generates simulated mining environment readings.
- **Edge** – Performs local anomaly detection and generates immediate safety alerts.
- **Fog** – Provides mine-level coordination and buffers data when Cloud connectivity is unavailable.
- **Cloud** – Stores historical sensor readings and alerts using SQLite.
- **SDN Network** – Connects the different layers using a virtual network created with Mininet/Containernet.
- **Edge Cache/CDN** – Maintains frequently accessed safety information at the Edge.

## Sensor Data

The simulated sensors generate:

- Gas concentration
- Temperature
- Vibration
- Humidity

Example reading:

```json
{
  "gas_ppm": 25.51,
  "temperature_c": 35.5,
  "vibration": 1.83,
  "humidity_percent": 66.2
}
```

## Edge Processing

The Edge layer checks sensor readings locally for dangerous conditions.

Examples:

- High gas level
- High temperature
- High vibration

When a dangerous condition is detected, the Edge immediately generates an alert before forwarding information to the Fog layer.

## Fog Processing

The Fog layer receives summarized information from the Edge.

It:

- Coordinates mine-level information
- Tracks received readings
- Tracks alerts
- Maintains a buffer for Cloud connectivity failures
- Forwards data to the Cloud when connectivity is available

## Cloud Storage

The Cloud layer stores historical readings in an SQLite database.

Stored information includes:

- Timestamp
- Gas level
- Temperature
- Vibration
- Humidity
- Danger status
- Alerts

## SDN / Containernet

The virtual network is created using Containernet and Mininet.

Topology:

Sensor -- s1 -- Edge -- s2 -- Fog -- s3 -- Cloud

IP addresses:

| Component | IP Address |
|---|---:|
| Sensor | 10.0.1.10 |
| Edge | 10.0.1.20 |
| Edge-Fog interface | 10.0.2.20 |
| Fog | 10.0.2.30 |
| Fog-Cloud interface | 10.0.3.30 |
| Cloud | 10.0.3.40 |

## Monitoring the System

The project includes a terminal-based monitoring program:

```bash
python3 /smart-mining/demo_monitor.py
```

The monitor displays:

- System status
- Latest sensor readings
- Edge decisions
- Edge cache information
- Fog status
- Cloud storage statistics
- Recent safety alerts


## Project Structure

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
│   └── Dockerfile
├── smart_mining_sdn.py
├── demo_monitor.py
└── readme.md
```
