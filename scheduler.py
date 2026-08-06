from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

from database import get_reminder_by_id
from reminder_service import send_reminder_to_recipient


scheduler = BackgroundScheduler(
    timezone="Asia/Kolkata"
)

def format_reminder_message(reminder):

    lines = [
        "📢 *Reminder*",
        "",
        f"📋 *{reminder.get('report_name', 'Reminder')}*"
    ]

    if reminder.get("task_title"):
        lines.extend([
            "",
            f"✅ *Task:* {reminder['task_title']}"
        ])

    if reminder.get("message"):
        lines.extend([
            "",
            reminder["message"]
        ])

    if reminder.get("details"):
        lines.extend([
            "",
            "📝 *Additional Details:*",
            reminder["details"]
        ])

    lines.extend([
        "",
        "Thank you."
    ])

    return "\n".join(lines)

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

    formatted_message = format_reminder_message(
        reminder
    )

    print("Formatted reminder message:")
    print(formatted_message)

    for recipient in recipients:

        chat_id = recipient["chat_id"]
        recipient_name = recipient["recipient_name"]

        print(
            f"Sending reminder {reminder_id} "
            f"to {recipient_name} ({chat_id})..."
        )

        result = send_reminder_to_recipient(
            chat_id=chat_id,
            message=formatted_message
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

def schedule_reminder(reminder):

    reminder_id = reminder["id"]
    job_id = reminder["job_id"]
    repeat_type = reminder["repeat_type"]

    schedule_time = reminder["schedule_time"]

    hour = schedule_time.hour
    minute = schedule_time.minute

    if repeat_type == "once":

        if not reminder["schedule_date"]:
            raise ValueError(
                "Schedule date is required for one-time reminder"
            )

        run_datetime = datetime.combine(
            reminder["schedule_date"],
            schedule_time
        )

        scheduler.add_job(
            func=send_reminder,
            trigger=DateTrigger(
                run_date=run_datetime
            ),
            args=[reminder_id],
            id=job_id,
            replace_existing=True
        )

        print(
            f"One-time reminder {reminder_id} "
            f"scheduled at {run_datetime}"
        )

    elif repeat_type == "daily":

        scheduler.add_job(
            func=send_reminder,
            trigger=CronTrigger(
                hour=hour,
                minute=minute,
                timezone="Asia/Kolkata"
            ),
            args=[reminder_id],
            id=job_id,
            replace_existing=True
        )

        print(
            f"Daily reminder {reminder_id} "
            f"scheduled at {hour:02d}:{minute:02d}"
        )

    elif repeat_type == "weekly":

        if not reminder["week_day"]:
            raise ValueError(
                "Weekday is required for weekly reminder"
            )
        
        weekday_map = {
            "monday": "mon",
            "tuesday": "tue",
            "wednesday": "wed",
            "thursday": "thu",
            "friday": "fri",
            "saturday": "sat",
            "sunday": "sun"
        }

        selected_weekday = reminder["week_day"].lower()

        cron_weekday = weekday_map.get(selected_weekday)

        if not cron_weekday:
            raise ValueError(
                f"Invalid weekday: {reminder['week_day']}"
            )

        scheduler.add_job(
            func=send_reminder,
            trigger=CronTrigger(
                day_of_week=cron_weekday,
                hour=hour,
                minute=minute,
                timezone="Asia/Kolkata"
            ),
            args=[reminder_id],
            id=job_id,
            replace_existing=True
        )

        print(
            f"Weekly reminder {reminder_id} "
            f"scheduled on {reminder['week_day']} "
            f"at {hour:02d}:{minute:02d}"
        )

    else:
        raise ValueError(
            f"Unsupported repeat type: {repeat_type}"
        )





