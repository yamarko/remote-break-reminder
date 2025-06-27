import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("remote_break_reminder")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.timezone = 'UTC'

app.conf.beat_schedule = {
    'check-reminders-every-minute': {
        'task': 'breaks.tasks.check_and_schedule_breaks',
        'schedule': crontab(minute='*/1'),
    },
}
