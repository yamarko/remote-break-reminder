from celery import shared_task


@shared_task
def send_break_reminder(user_id):
    print(f"Take a break! Reminder sent to user ID: {user_id}")
