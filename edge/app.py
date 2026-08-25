from flask import Flask, request, jsonify
from datetime import datetime
from collections import deque
import requests
import threading


app = Flask(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

GAS_THRESHOLD = 60.0
TEMPERATURE_THRESHOLD = 60.0
VIBRATION_THRESHOLD = 5.0

FOG_URL = "http://10.0.2.30:5000/edge-data"

# ============================================================
# LOCAL EDGE STATE
# ============================================================

latest_reading = None
latest_decision = None

alert_history = deque(maxlen=100)

# Cache for dashboard / local operation
reading_cache = deque(maxlen=100)


# ============================================================
# ANOMALY DETECTION
# ============================================================

def detect_danger(reading):

    dangers = []

    if reading.get("gas_ppm", 0) > GAS_THRESHOLD:
        dangers.append("HIGH GAS LEVEL")

    if reading.get("temperature_c", 0) > TEMPERATURE_THRESHOLD:
        dangers.append("HIGH TEMPERATURE")

    if reading.get("vibration", 0) > VIBRATION_THRESHOLD:
        dangers.append("HIGH VIBRATION")

    return dangers


# ============================================================
# SENSOR ENDPOINT
# ============================================================

@app.route("/sensor", methods=["POST"])
def receive_sensor_data():

    global latest_reading
    global latest_decision

    reading = request.get_json()

    if not reading:

        return jsonify({
            "status": "error",
            "message": "No sensor data received"
        }), 400


    # Store latest raw reading
    latest_reading = reading

    # Store in local cache
    reading_cache.append({
        "received_at": datetime.now().isoformat(),
        "reading": reading
    })


    # Perform local anomaly detection
    dangers = detect_danger(reading)

    is_danger = len(dangers) > 0


    latest_decision = {
        "timestamp": datetime.now().isoformat(),
        "danger": is_danger,
        "alerts": dangers
    }


    # ========================================================
    # LOCAL ALERT
    # ========================================================

    if is_danger:

        alert = {
            "timestamp": datetime.now().isoformat(),
            "alerts": dangers,
            "reading": reading
        }

        alert_history.append(alert)

        print("\n!!! EDGE ALERT !!!", flush=True)

        for danger in dangers:
            print(
                f"ALERT: {danger}",
                flush=True
            )

        print(
            f"Reading: {reading}",
            flush=True
        )

    else:

        print(
            f"EDGE: Normal reading - {reading}",
            flush=True
        )


    # ========================================================
    # SEND SUMMARIZED INFORMATION TO FOG
    # ========================================================

    fog_payload = {
        "timestamp": datetime.now().isoformat(),
        "source": "edge",
        "reading": reading,
        "danger": is_danger,
        "alerts": dangers
    }


    try:

        response = requests.post(
            FOG_URL,
            json=fog_payload,
            timeout=3
        )

        fog_status = response.json()

    except requests.exceptions.RequestException as error:

        fog_status = {
            "status": "fog_unreachable",
            "error": str(error)
        }


    return jsonify({

        "status": "processed",

        "edge": {
            "danger": is_danger,
            "alerts": dangers
        },

        "fog": fog_status

    })


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "service": "edge",
        "status": "running"
    })


# ============================================================
# DASHBOARD API - STATUS
# ============================================================

@app.route("/status", methods=["GET"])
def status():

    return jsonify({

        "service": "edge",

        "status": "running",

        "latest_reading": latest_reading,

        "latest_decision": latest_decision,

        "cache_size": len(reading_cache),

        "alert_count": len(alert_history)

    })


# ============================================================
# DASHBOARD API - ALERTS
# ============================================================

@app.route("/alerts", methods=["GET"])
def alerts():

    return jsonify({
        "count": len(alert_history),
        "alerts": list(alert_history)
    })


# ============================================================
# DASHBOARD API - CACHE
# ============================================================

@app.route("/cache", methods=["GET"])
def cache():

    return jsonify({
        "size": len(reading_cache),
        "readings": list(reading_cache)
    })

# ============================================================
# EDGE SAFETY CACHE / CDN
# ============================================================

safety_cache_hits = 0
safety_cache_misses = 0


@app.route("/safety", methods=["GET"])
def safety():

    global safety_cache_hits
    global safety_cache_misses

    # --------------------------------------------------------
    # Cache MISS
    # --------------------------------------------------------
    if latest_reading is None:

        safety_cache_misses += 1

        return jsonify({
            "status": "cache_miss",
            "cached": False,
            "message": "No safety information available yet"
        }), 404

    # --------------------------------------------------------
    # Cache HIT
    # --------------------------------------------------------
    safety_cache_hits += 1

    recent_readings = list(reading_cache)[-10:]
    recent_alerts = list(alert_history)[-10:]

    return jsonify({

        "status": "cache_hit",

        "cached": True,

        "source": "edge",

        "cache": {
            "type": "edge_safety_cache",
            "hits": safety_cache_hits,
            "misses": safety_cache_misses,
            "entries": len(reading_cache)
        },

        "latest_reading": latest_reading,

        "latest_decision": latest_decision,

        "recent_alerts": recent_alerts,

        "recent_readings": recent_readings

    })
    
# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True
    )
