from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

from database import get_reminder_by_id
from reminder_service import send_reminder_to_recipient


scheduler = BackgroundScheduler(
    timezone="Asia/Kolkata"
)


def start_scheduler():

    if not scheduler.running:
        scheduler.start()

        print("Reminder scheduler started.")


def stop_scheduler():

    if scheduler.running:
        scheduler.shutdown(wait=False)

        print("Reminder scheduler stopped.")


def send_reminder(reminder_id):

    print(f"Executing reminder: {reminder_id}")

    reminder = get_reminder_by_id(reminder_id)

    if not reminder:
        print(f"Reminder {reminder_id} not found.")
        return

    if not reminder["is_active"]:
        print(
            f"Reminder {reminder_id} is disabled. "
            "Message not sent."
        )
        return

    recipients = reminder["recipients"]

    if not recipients:
        print(
            f"Reminder {reminder_id} has no recipients."
        )
        return

    for recipient in recipients:

        chat_id = recipient["chat_id"]
        recipient_name = recipient["recipient_name"]

        print(
            f"Sending reminder {reminder_id} "
            f"to {recipient_name} ({chat_id})..."
        )

        result = send_reminder_to_recipient(
            chat_id=chat_id,
            message=reminder["message"]
        )

        if result["success"]:
            print(
                f"Reminder sent successfully to "
                f"{recipient_name}."
            )
        else:
            print(
                f"Failed to send reminder to "
                f"{recipient_name}: {result}"
            )


def schedule_one_time_reminder(reminder):

    run_datetime = datetime.combine(
        reminder["schedule_date"],
        reminder["schedule_time"]
    )

    scheduler.add_job(
        func=send_reminder,
        trigger=DateTrigger(
            run_date=run_datetime
        ),
        args=[reminder["id"]],
        id=reminder["job_id"],
        replace_existing=True
    )

    print(
        f"Scheduled reminder {reminder['id']} "
        f"at {run_datetime}"
    )