import json
import os
import time
from datetime import datetime

import requests


# ============================================================
# SMART MINING DEMONSTRATION MONITOR
# ============================================================

EDGE_URL = None
FOG_URL = None
CLOUD_URL = None

REFRESH_SECONDS = 3
TIMEOUT = 2


# ============================================================
# DOCKER PORT DISCOVERY
# ============================================================

def get_container_port(container_name):
    """
    Find the current host port mapped to container port 5000.

    Example:
        5000/tcp -> 0.0.0.0:32777

    Returns:
        "32777"
        or None if the container is unavailable.
    """

    try:
        result = os.popen(
            f"docker port {container_name} 5000/tcp 2>/dev/null"
        ).read().strip()

        if not result:
            return None

        for line in result.splitlines():

            line = line.strip()

            if ":" in line:

                port = line.rsplit(":", 1)[-1]

                if port.isdigit():
                    return port

    except Exception:
        pass

    return None


def discover_service_urls():
    """
    Automatically discover the current Docker-published
    ports for Edge, Fog and Cloud.
    """

    edge_port = get_container_port("mn.edge")
    fog_port = get_container_port("mn.fog")
    cloud_port = get_container_port("mn.cloud")

    return {
        "edge":
            f"http://127.0.0.1:{edge_port}"
            if edge_port else None,

        "fog":
            f"http://127.0.0.1:{fog_port}"
            if fog_port else None,

        "cloud":
            f"http://127.0.0.1:{cloud_port}"
            if cloud_port else None
    }


# ============================================================
# HTTP HELPERS
# ============================================================

def get_json(url):

    if not url:
        return {
            "_error": "Service unavailable"
        }

    try:

        response = requests.get(
            url,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except Exception as error:

        return {
            "_error": str(error)
        }


def is_online(data):

    return (
        isinstance(data, dict)
        and "_error" not in data
    )


# ============================================================
# FORMATTING
# ============================================================

def clear_screen():

    os.system("clear")


def value(data, key, default=" "):

    if not isinstance(data, dict):
        return default

    result = data.get(key, default)

    if result is None:
        return default

    return result


def print_line():

    print("-" * 64)


def print_status(name, ip, data):

    if is_online(data):

        print(
            f"{name:<12} {ip:<16} "
            "\033[92mONLINE\033[0m"
        )

    else:

        print(
            f"{name:<12} {ip:<16} "
            "\033[91mOFFLINE\033[0m"
        )


# ============================================================
# MAIN MONITOR
# ============================================================

def monitor():

    global EDGE_URL
    global FOG_URL
    global CLOUD_URL

    while True:

        # ====================================================
        # AUTOMATICALLY DISCOVER CURRENT DOCKER PORTS
        # ====================================================

        urls = discover_service_urls()

        EDGE_URL = urls["edge"]
        FOG_URL = urls["fog"]
        CLOUD_URL = urls["cloud"]

        # ====================================================
        # GET DATA FROM ALL APPLICATION LAYERS
        # ====================================================

        edge_status = get_json(
            f"{EDGE_URL}/status"
            if EDGE_URL else None
        )

        edge_alerts = get_json(
            f"{EDGE_URL}/alerts"
            if EDGE_URL else None
        )

        edge_safety = get_json(
            f"{EDGE_URL}/safety"
            if EDGE_URL else None
        )

        fog_status = get_json(
            f"{FOG_URL}/status"
            if FOG_URL else None
        )

        cloud_status = get_json(
            f"{CLOUD_URL}/status"
            if CLOUD_URL else None
        )

        cloud_alerts = get_json(
            f"{CLOUD_URL}/alerts"
            if CLOUD_URL else None
        )

        # ====================================================
        # CLEAR TERMINAL
        # ====================================================

        clear_screen()

        print()
        print("=" * 64)
        print("              SMART MINING SAFETY MONITOR")
        print("                 EDGE FOG CLOUD + SDN")
        print("=" * 64)

        print(
            "Updated:",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        # ====================================================
        # 1. NETWORK / APPLICATION STATUS
        # ====================================================

        print()
        print("[1] SYSTEM STATUS")
        print_line()

        print_status(
            "SENSOR",
            "10.0.1.10",
            edge_status
        )

        print_status(
            "EDGE",
            "10.0.1.20",
            edge_status
        )

        print_status(
            "FOG",
            "10.0.2.30",
            fog_status
        )

        print_status(
            "CLOUD",
            "10.0.3.40",
            cloud_status
        )

        print()
        print(
            "SDN PATH : "
            "Sensor -- s1 -- Edge -- s2 -- Fog -- s3 -- Cloud"
        )

        # ====================================================
        # 2. SENSOR DATA
        # ====================================================

        print()
        print("[2] LATEST SENSOR READING")
        print_line()

        reading = edge_status.get(
            "latest_reading"
        )

        if reading:

            print(
                f"Timestamp       : "
                f"{value(reading, 'timestamp')}"
            )

            print(
                f"Gas             : "
                f"{value(reading, 'gas_ppm')} ppm"
            )

            print(
                f"Temperature     : "
                f"{value(reading, 'temperature_c')} C"
            )

            print(
                f"Vibration       : "
                f"{value(reading, 'vibration')}"
            )

            print(
                f"Humidity        : "
                f"{value(reading, 'humidity_percent')} %"
            )

        else:

            print("No sensor data available.")

        # ====================================================
        # 3. EDGE PROCESSING
        # ====================================================

        print()
        print("[3] EDGE PROCESSING")
        print_line()

        decision = edge_status.get(
            "latest_decision"
        )

        if decision:

            danger = decision.get(
                "danger",
                False
            )

            alerts = decision.get(
                "alerts",
                []
            )

            if danger:

                print(
                    "Decision        : "
                    "\033[91mDANGER\033[0m"
                )

            else:

                print(
                    "Decision        : "
                    "\033[92mNORMAL\033[0m"
                )

            print(
                f"Danger flag     : {danger}"
            )

            if alerts:

                print("Alerts          :")

                for alert in alerts:

                    print(
                        f"                  "
                        f"\033[91m[!] {alert}\033[0m"
                    )

            else:

                print("Alerts          : NONE")

        else:

            print("No Edge decision available.")

        print(
            f"Cache entries   : "
            f"{value(edge_status, 'cache_size')}"
        )

        print(
            f"Alert count     : "
            f"{value(edge_status, 'alert_count')}"
        )

        # ====================================================
        # 4. EDGE CACHE / CDN
        # ====================================================

        print()
        print("[4] EDGE SAFETY CACHE / CDN")
        print_line()

        if is_online(edge_safety):

            cache_info = edge_safety.get(
                "cache",
                {}
            )

            print(
                "Status          : "
                f"\033[92m{value(edge_safety, 'status')}\033[0m"
            )

            print(
                "Source          : "
                f"{value(edge_safety, 'source')}"
            )

            print(
                "Cached          : "
                f"{value(edge_safety, 'cached')}"
            )

            print(
                "Cache hits      : "
                f"{value(cache_info, 'hits')}"
            )

            print(
                "Cache misses    : "
                f"{value(cache_info, 'misses')}"
            )

            print(
                "Cached entries  : "
                f"{value(cache_info, 'entries')}"
            )

        else:

            print(
                "\033[91mSafety cache unavailable\033[0m"
            )

        # ====================================================
        # 5. FOG PROCESSING
        # ====================================================

        print()
        print("[5] FOG COORDINATION")
        print_line()

        if is_online(fog_status):

            print(
                "Readings received : "
                f"{value(fog_status, 'received_readings')}"
            )

            print(
                "Alerts received   : "
                f"{value(fog_status, 'alert_count')}"
            )

            print(
                "Buffer size       : "
                f"{value(fog_status, 'buffer_size')}"
            )

            print(
                "Cloud connection  : "
                f"{value(fog_status, 'cloud_status')}"
            )

        else:

            print(
                "\033[91mFog unavailable\033[0m"
            )

        # ====================================================
        # 6. CLOUD STORAGE
        # ====================================================

        print()
        print("[6] CLOUD STORAGE")
        print_line()

        if is_online(cloud_status):

            print(
                "Database          : "
                f"\033[92m{value(cloud_status, 'database')}\033[0m"
            )

            print(
                "Total readings    : "
                f"{value(cloud_status, 'total_readings')}"
            )

            print(
                "Total alerts      : "
                f"{value(cloud_status, 'total_alerts')}"
            )

        else:

            print(
                "\033[91mCloud unavailable\033[0m"
            )

        # ====================================================
        # 7. RECENT ALERTS
        # ====================================================

        print()
        print("[7] RECENT SAFETY ALERTS")
        print_line()

        alerts = []

        if isinstance(edge_alerts, dict):

            alerts.extend(
                edge_alerts.get(
                    "alerts",
                    []
                )
            )

        if isinstance(cloud_alerts, dict):

            alerts.extend(
                cloud_alerts.get(
                    "alerts",
                    []
                )
            )

        # ----------------------------------------------------
        # Remove duplicate timestamps
        # ----------------------------------------------------

        unique_alerts = []

        seen = set()

        for alert in alerts:

            timestamp = alert.get(
                "timestamp"
            )

            if timestamp not in seen:

                seen.add(timestamp)

                unique_alerts.append(
                    alert
                )

        unique_alerts = unique_alerts[-5:]

        if unique_alerts:

            for alert in reversed(
                unique_alerts
            ):

                timestamp = value(
                    alert,
                    "timestamp"
                )

                alert_names = alert.get(
                    "alerts",
                    []
                )

                if isinstance(
                    alert_names,
                    list
                ):

                    alert_text = ", ".join(
                        alert_names
                    )

                else:

                    alert_text = str(
                        alert_names
                    )

                print(
                    f"{timestamp}"
                )

                print(
                    f"  \033[91m[!] "
                    f"{alert_text}\033[0m"
                )

        else:

            print(
                "\033[92mNo recent alerts.\033[0m"
            )

        # ====================================================
        # FOOTER
        # ====================================================

        print()
        print("=" * 64)

        print(
            " Monitoring refresh: "
            f"{REFRESH_SECONDS}s"
        )

        print(
            " Press Ctrl+C to stop"
        )

        print("=" * 64)

        time.sleep(
            REFRESH_SECONDS
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:

        monitor()

    except KeyboardInterrupt:

        print()
        print("Monitoring stopped.")