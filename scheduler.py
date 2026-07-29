print("scheduler.py imported")

from apscheduler.schedulers.background import BackgroundScheduler
from reminder_service import send_reminder_to_all_groups


def send_daily_reminder():

    message = (
        "📢 Reminder\n\n"
        "Please send today's details"
    )

    result = send_reminder_to_all_groups(message)

    print("Reminder sent:", result)


scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

scheduler.add_job(
    send_daily_reminder,
    trigger="cron",
    hour=15,
    minute=30,
)

scheduler.start()
print("Scheduler started successfully")

