from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class BreakInterval(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interval_minutes = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(5), MaxValueValidator(480)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - every {self.interval_minutes} min"
