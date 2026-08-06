import os
import smtplib

from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM")
EMAIL_TO = os.getenv("ALERT_EMAIL_TO")
EMAIL_PASSWORD = os.getenv(
    "ALERT_EMAIL_APP_PASSWORD"
)


def send_alert_email(
    subject: str,
    body: str,
    attachment_path: str | None = None
):

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = EMAIL_FROM
    message["To"] = EMAIL_TO

    message.set_content(body)

    if attachment_path:

        path = Path(attachment_path)

        if path.exists():

            message.add_attachment(
                path.read_bytes(),
                maintype="image",
                subtype="png",
                filename=path.name
            )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:

        smtp.login(
            EMAIL_FROM,
            EMAIL_PASSWORD
        )

        smtp.send_message(message)

    print("Alert email sent successfully.")