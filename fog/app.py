from flask import Flask, request, jsonify
from datetime import datetime
from collections import deque
import requests
import threading
import time


app = Flask(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

CLOUD_URL = "http://10.0.3.40:5000/cloud-data"

# ============================================================
# FOG STATE
# ============================================================

received_readings = deque(maxlen=500)

cloud_buffer = deque(maxlen=1000)

alert_count = 0

cloud_status = "UNKNOWN"


# ============================================================
# EDGE DATA ENDPOINT
# ============================================================

@app.route("/edge-data", methods=["POST"])
def receive_edge_data():

    global alert_count
    global cloud_status

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "No Edge data received"
        }), 400


    # Store incoming data
    received_readings.append(data)


    # Count alerts
    if data.get("danger", False):

        alert_count += len(
            data.get("alerts", [])
        )


    # ========================================================
    # TRY TO SEND TO CLOUD
    # ========================================================

    try:

        response = requests.post(
            CLOUD_URL,
            json=data,
            timeout=3
        )

        cloud_status = "ONLINE"

        print(
            "FOG: Data sent to Cloud",
            flush=True
        )

        return jsonify({

            "status": "processed",

            "cloud": "sent"

        })


    except requests.exceptions.RequestException as error:

        cloud_status = "OFFLINE"

        # Buffer for later delivery
        cloud_buffer.append(data)

        print(
            "FOG: Cloud unavailable - data buffered",
            flush=True
        )

        return jsonify({

            "status": "buffered",

            "cloud": "offline",

            "buffer_size": len(cloud_buffer)

        })


# ============================================================
# BUFFER FLUSH
# ============================================================

def flush_buffer():

    global cloud_status

    while True:

        if len(cloud_buffer) > 0:

            try:

                data = cloud_buffer[0]

                response = requests.post(
                    CLOUD_URL,
                    json=data,
                    timeout=3
                )

                cloud_buffer.popleft()

                cloud_status = "ONLINE"

                print(
                    "FOG: Buffered data sent to Cloud",
                    flush=True
                )

            except requests.exceptions.RequestException:

                cloud_status = "OFFLINE"


        time.sleep(2)


# ============================================================
# HEALTH
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "service": "fog",
        "status": "running"
    })


# ============================================================
# DASHBOARD API - STATUS
# ============================================================

@app.route("/status", methods=["GET"])
def status():

    return jsonify({

        "service": "fog",

        "status": "running",

        "cloud_status": cloud_status,

        "received_readings":
            len(received_readings),

        "alert_count":
            alert_count,

        "buffer_size":
            len(cloud_buffer)

    })


# ============================================================
# DASHBOARD API - DATA
# ============================================================

@app.route("/data", methods=["GET"])
def data():

    return jsonify({

        "count":
            len(received_readings),

        "readings":
            list(received_readings)

    })


# ============================================================
# DASHBOARD API - BUFFER
# ============================================================

@app.route("/buffer", methods=["GET"])
def buffer():

    return jsonify({

        "size":
            len(cloud_buffer),

        "buffer":
            list(cloud_buffer)

    })


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    threading.Thread(
        target=flush_buffer,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True
    )
