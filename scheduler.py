from apscheduler.schedulers.background import BackgroundScheduler


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

from datetime import datetime


def send_reminder(reminder_id):

    print(f"Executing reminder: {reminder_id}")

    # Later:
    # 1. Read reminder from database
    # 2. Get recipients
    # 3. Send WhatsApp message using WAHA

from apscheduler.triggers.date import DateTrigger

from datetime import datetime


def schedule_one_time_reminder(reminder):

    run_datetime = datetime.combine(
        reminder["schedule_date"],
        reminder["schedule_time"]
    )

    scheduler.add_job(
        func=send_reminder,
        trigger="date",
        run_date=run_datetime,
        args=[reminder["id"]],
        id=reminder["job_id"],
        replace_existing=True
    )

    print(
        f"Scheduled reminder {reminder['id']} "
        f"at {run_datetime}"
    )