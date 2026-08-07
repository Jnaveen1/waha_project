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

FASTAPI_HEALTH_URL = os.getenv(
    "FASTAPI_HEALTH_URL",
    "http://127.0.0.1:8000/"
)

last_fastapi_status = None
last_waha_service_status = None

WAHA_API_KEY = os.getenv(
    "WAHA_API_KEY"
)

CHECK_INTERVAL_SECONDS = 10
last_status = None
last_qr_hash = None

def check_fastapi():

    try:
        response = requests.get(
            FASTAPI_HEALTH_URL,
            timeout=10
        )

        return response.status_code == 200

    except requests.RequestException:
        return False

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
    global last_fastapi_status
    global last_waha_service_status

    current_time = datetime.now().strftime(
        "%d-%m-%Y %I:%M:%S %p"
    )


    # --------------------------------
    # 1. Check FastAPI
    # --------------------------------

    fastapi_working = check_fastapi()

    print(
        f"{current_time} - FastAPI: "
        f"{'WORKING' if fastapi_working else 'DOWN'}"
    )

    if fastapi_working != last_fastapi_status:

        if not fastapi_working:

            send_alert_email(
                subject="Reminder Application Down",
                body=(
                    "The FastAPI reminder application "
                    "is not responding.\n\n"
                    f"Detected at: {current_time}\n\n"
                    "Scheduled reminder APIs and the "
                    "frontend may not be available."
                )
            )

        elif last_fastapi_status is False:

            send_alert_email(
                subject="Reminder Application Restored",
                body=(
                    "The FastAPI reminder application "
                    "is working again.\n\n"
                    f"Restored at: {current_time}"
                )
            )

        last_fastapi_status = fastapi_working


    # --------------------------------
    # 2. Check WAHA service
    # --------------------------------

    waha_service_working = check_waha_service()

    print(
        f"{current_time} - WAHA Service: "
        f"{'WORKING' if waha_service_working else 'DOWN'}"
    )

    if waha_service_working != last_waha_service_status:

        if not waha_service_working:

            send_alert_email(
                subject="WAHA Service Down",
                body=(
                    "The watchdog cannot connect "
                    "to the WAHA service.\n\n"
                    f"WAHA URL: {WAHA_BASE_URL}\n"
                    f"Detected at: {current_time}\n\n"
                    "Please check Docker Desktop "
                    "and the WAHA container."
                )
            )

        elif last_waha_service_status is False:

            send_alert_email(
                subject="WAHA Service Restored",
                body=(
                    "The WAHA service is reachable "
                    "again.\n\n"
                    f"Restored at: {current_time}"
                )
            )

        last_waha_service_status = (
            waha_service_working
        )


    # If WAHA itself is down,
    # don't try to check the session.
    if not waha_service_working:
        return


    # --------------------------------
    # 3. Check WhatsApp session
    # --------------------------------

    status = get_session_status()

    print(
        f"{current_time} - WhatsApp Session: "
        f"{status}"
    )


    # QR required
    if status == "SCAN_QR_CODE":

        qr_path, qr_hash = fetch_qr_code()

        if (
            qr_hash
            and qr_hash != last_qr_hash
        ):

            send_alert_email(
                subject="WhatsApp QR Scan Required",
                body=(
                    "A fresh WhatsApp QR code "
                    "is attached.\n\n"
                    f"Session: {WAHA_SESSION}\n"
                    f"Generated at: {current_time}\n\n"
                    "Open this email immediately "
                    "on another screen and scan "
                    "it using:\n\n"
                    "WhatsApp → Linked Devices → "
                    "Link a Device.\n\n"
                    "Important: This QR expires "
                    "quickly."
                ),
                attachment_path=qr_path
            )

            last_qr_hash = qr_hash

        last_status = status

        return


    # No state change
    if status == last_status:
        return


    print(
        f"WhatsApp status changed: "
        f"{last_status} -> {status}"
    )


    if status == "WORKING":

        if last_status is not None:

            send_alert_email(
                subject="WhatsApp Connection Restored",
                body=(
                    "The WhatsApp session is "
                    "working normally again.\n\n"
                    f"Session: {WAHA_SESSION}\n"
                    f"Restored at: {current_time}"
                )
            )

        last_qr_hash = None


    elif status is None:

        send_alert_email(
            subject="WhatsApp Session Unavailable",
            body=(
                "WAHA is running, but the "
                "WhatsApp session status could "
                "not be determined.\n\n"
                f"Session: {WAHA_SESSION}\n"
                f"Detected at: {current_time}"
            )
        )


    else:

        send_alert_email(
            subject="WhatsApp Session Problem",
            body=(
                "The WhatsApp session is not "
                "working normally.\n\n"
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

def check_waha_service():

    headers = {
        "X-Api-Key": WAHA_API_KEY
    }

    try:
        response = requests.get(
            f"{WAHA_BASE_URL}/health",
            headers=headers,
            timeout=10
        )

        return response.status_code == 200

    except requests.RequestException:
        return False

if __name__ == "__main__":
    run_monitor()

