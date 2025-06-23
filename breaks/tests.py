import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse
from .models import BreakInterval


@pytest.fixture
def user(db):
    return User.objects.create_user(username='test_user', password='pass123')


@pytest.mark.django_db
class TestBreakIntervalModel:

    def test_break_interval_creation(self, user):
        interval = BreakInterval.objects.create(user=user)

        assert interval.pk is not None
        assert interval.interval_minutes == 60
        assert str(interval) == "test_user - every 60 min"

    def test_invalid_intervals(self, user):
        inv_intervals = [3, 500, -10, "abc"]

        for value in inv_intervals:
            interval = BreakInterval(user=user, interval_minutes=value)
            with pytest.raises(ValidationError):
                interval.full_clean()

    def test_unique_user_constraint(self, user):
        BreakInterval.objects.create(user=user)

        with pytest.raises(IntegrityError):
            BreakInterval.objects.create(user=user, interval_minutes=30)

    def test_user_deletion_cascades(self, user):
        BreakInterval.objects.create(user=user)
        assert BreakInterval.objects.filter(user=user).exists()

        user.delete()

        assert not BreakInterval.objects.filter(user_id=user.id).exists()


@pytest.mark.django_db
class TestAuth:

    def test_register(self, client):
        response = client.post(reverse("register"), {
            "username": "test_username",
            "password1": "testpass11",
            "password2": "testpass11"})

        assert response.status_code == 302
        assert response.url == reverse("login")

    def test_login(self, client, user):
        response = client.post(reverse("login"), {
            "username": "test_user",
            "password": "pass123"
        })

        assert response.status_code == 200
        assert b"Login successful!" in response.content

    def test_logout(self, client, user):
        assert client.login(username="test_user", password="pass123")

        response = client.post(reverse("logout"))

        assert response.status_code == 200
        assert b"Logout successful!" in response.content
