import logging
from datetime import timedelta
from celery import shared_task

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone

from .models import BreakInterval, BreakLog


logger = logging.getLogger(__name__)


@shared_task
def send_break_reminder(user_id):
    try:
        user = User.objects.get(id=user_id)
        BreakLog.objects.create(user=user)
        logger.info(f"Break reminder logged for {user.username}")

        send_mail(
            subject="⏰ Time for a break!",
            message="Hey! You've been working hard. Take a few minutes to stretch or rest.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )

        logger.info(f"Email reminder sent to {user.email}")

    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist.")


@shared_task
def check_and_schedule_breaks():
    now = timezone.now()

    for interval in BreakInterval.objects.all():
        user = interval.user
        last_break = (
            BreakLog.objects.filter(user=user).order_by('-triggered_at').first()
        )

        interval_time = timedelta(minutes=interval.interval_minutes)
        time_since_last = now - last_break.triggered_at if last_break else None

        if not last_break or time_since_last >= interval_time:
            send_break_reminder.delay(user.id)
