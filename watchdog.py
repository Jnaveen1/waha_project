import os
import time
from datetime import datetime
import hashlib

import requests
from dotenv import load_dotenv

from email_service import send_alert_email
from pathlib import Path

load_dotenv()

WAHA_BASE_URL = os.getenv(
    "WAHA_BASE_URL",
    "http://localhost:3000"
)

WAHA_SESSION = os.getenv(
    "WAHA_SESSION",
    "default"
)

WAHA_API_KEY = os.getenv(
    "WAHA_API_KEY"
)

CHECK_INTERVAL_SECONDS = 10
last_status = None
last_qr_hash = None

def get_session_status():

    headers = {
        "X-Api-Key": WAHA_API_KEY
    }

    try:
        response = requests.get(
            f"{WAHA_BASE_URL}/api/sessions/{WAHA_SESSION}",
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        return data.get("status")

    except requests.RequestException as error:

        print(
            "Unable to check WAHA session:",
            error
        )

        return None

def fetch_qr_code():

    qr_path = Path("latest_waha_qr.png")

    headers = {
        "X-Api-Key": WAHA_API_KEY,
        "Accept": "image/png"
    }

    try:
        response = requests.get(
            (
                f"{WAHA_BASE_URL}/api/"
                f"{WAHA_SESSION}/auth/qr"
            ),
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "image" not in content_type:
            print(
                "QR endpoint did not return an image."
            )
            return None, None

        qr_bytes = response.content

        qr_hash = hashlib.sha256(
            qr_bytes
        ).hexdigest()

        qr_path.write_bytes(qr_bytes)

        return str(qr_path), qr_hash

    except requests.RequestException as error:
        print(
            "Unable to fetch WAHA QR code:",
            error
        )

        return None, None

def monitor_once():

    global last_status
    global last_qr_hash

    status = get_session_status()

    current_time = datetime.now().strftime(
        "%d-%m-%Y %I:%M:%S %p"
    )

    print(
        f"{current_time} - WAHA status: {status}"
    )

    if status == "SCAN_QR_CODE":

        qr_path, qr_hash = fetch_qr_code()

        # Send only when WAHA generates a different QR.
        if qr_hash and qr_hash != last_qr_hash:

            send_alert_email(
                subject="WhatsApp QR Scan Required",
                body=(
                    "A fresh WhatsApp QR code is attached.\n\n"
                    f"Session: {WAHA_SESSION}\n"
                    f"Generated at: {current_time}\n\n"
                    "Open this email immediately on another "
                    "screen and scan it using:\n"
                    "WhatsApp → Linked Devices → "
                    "Link a Device.\n\n"
                    "Important: This QR expires quickly."
                ),
                attachment_path=qr_path
            )

            last_qr_hash = qr_hash

        last_status = status
        return

    if status == last_status:
        return

    print(
        f"Status changed: "
        f"{last_status} -> {status}"
    )

    if status == "WORKING":

        send_alert_email(
            subject="WAHA Connection Restored",
            body=(
                "The WhatsApp reminder system "
                "is working normally again.\n\n"
                f"Session: {WAHA_SESSION}\n"
                f"Restored at: {current_time}"
            )
        )

        last_qr_hash = None

    elif status is None:

        send_alert_email(
            subject="WAHA Service Unreachable",
            body=(
                "The watchdog cannot connect to WAHA.\n\n"
                f"Detected at: {current_time}\n"
                "Check Docker Desktop and the WAHA container."
            )
        )

    else:

        send_alert_email(
            subject="WAHA Session Problem",
            body=(
                "The WhatsApp session is not working.\n\n"
                f"Session: {WAHA_SESSION}\n"
                f"Status: {status}\n"
                f"Detected at: {current_time}"
            )
        )

    last_status = status

def run_monitor():

    print("WAHA watchdog started.")

    while True:

        monitor_once()

        time.sleep(
            CHECK_INTERVAL_SECONDS
        )


if __name__ == "__main__":
    run_monitor()