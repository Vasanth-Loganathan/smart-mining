from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import threading


app = Flask(__name__)


DATABASE = "mining.db"


# ============================================================
# DATABASE
# ============================================================

def get_db():

    connection = sqlite3.connect(
        DATABASE,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS readings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT,

            gas_ppm REAL,

            temperature_c REAL,

            vibration REAL,

            humidity_percent REAL,

            danger INTEGER,

            alerts TEXT

        )
    """)

    connection.commit()

    connection.close()


# ============================================================
# RECEIVE DATA FROM FOG
# ============================================================

@app.route("/cloud-data", methods=["POST"])
def receive_data():

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "No data received"
        }), 400


    reading = data.get(
        "reading",
        {}
    )


    alerts = ",".join(
        data.get("alerts", [])
    )


    connection = get_db()


    connection.execute("""

        INSERT INTO readings (

            timestamp,
            gas_ppm,
            temperature_c,
            vibration,
            humidity_percent,
            danger,
            alerts

        )

        VALUES (?, ?, ?, ?, ?, ?, ?)

    """, (

        reading.get("timestamp"),

        reading.get("gas_ppm"),

        reading.get("temperature_c"),

        reading.get("vibration"),

        reading.get("humidity_percent"),

        int(
            data.get("danger", False)
        ),

        alerts

    ))


    connection.commit()

    connection.close()


    print(
        "CLOUD: Historical reading stored",
        flush=True
    )


    return jsonify({

        "status": "stored"

    })


# ============================================================
# HEALTH
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({

        "service": "cloud",

        "status": "running",

        "database": "connected"

    })


# ============================================================
# DASHBOARD API - STATUS
# ============================================================

@app.route("/status", methods=["GET"])
def status():

    connection = get_db()

    count = connection.execute(
        "SELECT COUNT(*) AS count FROM readings"
    ).fetchone()["count"]


    alerts = connection.execute(
        "SELECT COUNT(*) AS count FROM readings WHERE danger = 1"
    ).fetchone()["count"]


    connection.close()


    return jsonify({

        "service": "cloud",

        "status": "running",

        "database": "connected",

        "total_readings": count,

        "total_alerts": alerts

    })


# ============================================================
# DASHBOARD API - HISTORICAL DATA
# ============================================================

@app.route("/readings", methods=["GET"])
def readings():

    connection = get_db()


    rows = connection.execute("""

        SELECT *

        FROM readings

        ORDER BY id DESC

        LIMIT 100

    """).fetchall()


    connection.close()


    return jsonify({

        "count": len(rows),

        "readings": [

            dict(row)

            for row in rows

        ]

    })


# ============================================================
# DASHBOARD API - ALERTS
# ============================================================

@app.route("/alerts", methods=["GET"])
def alerts():

    connection = get_db()


    rows = connection.execute("""

        SELECT *

        FROM readings

        WHERE danger = 1

        ORDER BY id DESC

        LIMIT 100

    """).fetchall()


    connection.close()


    return jsonify({

        "count": len(rows),

        "alerts": [

            dict(row)

            for row in rows

        ]

    })


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    initialize_database()

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True
    )
