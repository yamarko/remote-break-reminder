import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch
from .models import BreakInterval, BreakLog
from breaks.tasks import send_break_reminder, check_and_schedule_breaks
from breaks.utils import get_reminder_content


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="test_user",
        email="test@example.com",
        password="pass123")


@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)

    return client


@pytest.fixture
def create_interval(user):
    return BreakInterval.objects.create(user=user)


@pytest.mark.django_db
class TestBreakIntervalModel:

    def test_break_interval_creation(self, create_interval):
        interval = create_interval

        assert interval.pk is not None
        assert interval.interval_minutes == 60
        assert str(interval) == "test_user - every 60 min"

    def test_invalid_intervals(self, user):
        inv_intervals = [3, 500, -10, "abc"]

        for value in inv_intervals:
            interval = BreakInterval(user=user, interval_minutes=value)
            with pytest.raises(ValidationError):
                interval.full_clean()

    def test_unique_user_constraint(self, user, create_interval):
        with pytest.raises(IntegrityError):
            BreakInterval.objects.create(user=user, interval_minutes=30)

    def test_user_deletion_cascades(self, user, create_interval):
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


@pytest.mark.django_db
class TestBreakIntervalAPI:

    def test_get_interval(self, authenticated_client, user, create_interval):
        response = authenticated_client.get(
            reverse("break-interval-detail", kwargs={"pk": user.breakinterval.pk})
        )

        assert response.status_code == 200
        assert response.data["interval_minutes"] == 60

    def test_create_interval(self, authenticated_client, user):
        data = {"interval_minutes": 90}

        response = authenticated_client.post(reverse("break-interval-list"), data)

        assert response.status_code == 201
        assert BreakInterval.objects.count() == 1
        assert BreakInterval.objects.first().user == user

    def test_partial_update_interval(self, authenticated_client, user, create_interval):
        partial_data = {"interval_minutes": 75}

        response = authenticated_client.patch(
            reverse("break-interval-detail", kwargs={"pk": user.breakinterval.pk}),
            partial_data,
        )

        assert response.status_code == 200

        user.breakinterval.refresh_from_db()
        assert user.breakinterval.interval_minutes == 75

    def test_delete_interval(self, authenticated_client, user, create_interval):
        response = authenticated_client.delete(
            reverse("break-interval-detail", kwargs={"pk": user.breakinterval.pk})
        )

        assert response.status_code == 204
        assert BreakInterval.objects.count() == 0


@pytest.mark.django_db
class TestBreakReminderTasks:

    @patch("breaks.tasks.send_mail")
    def test_send_reminder(self, mock_send, user, create_interval):
        send_break_reminder(user.id)

        assert BreakLog.objects.filter(user=user).exists()
        mock_send.assert_called_once()

    @patch("breaks.tasks.logger")
    def test_send_reminder_invalid_user(self, mock_logger):
        send_break_reminder(9999)
        mock_logger.error.assert_called_once_with("User with ID 9999 does not exist.")

    @patch("breaks.tasks.send_break_reminder.delay")
    def test_check_and_trigger(self, mock_delay, user, create_interval):
        check_and_schedule_breaks()

        mock_delay.assert_called_once_with(user.id)

    def test_get_reminder_content(self):
        subject, message = get_reminder_content()
        assert isinstance(subject, str) and subject
        assert isinstance(message, str) and message


@pytest.mark.django_db
class TestLastBreakLogsAPI:

    endpoint = reverse('break-log-list')

    def test_auth_required(self, client):
        response = client.get(self.endpoint)
        assert response.status_code == 403

    def test_all_breaks_ordered(self, authenticated_client, user):
        for i in range(6):
            BreakLog.objects.create(user=user)

        response = authenticated_client.get(self.endpoint)
        assert response.status_code == 200
        assert len(response.data) == 6

        times = [log['triggered_at'] for log in response.data]
        assert times == sorted(times, reverse=True)

    def test_no_breaks(self, authenticated_client):
        response = authenticated_client.get(self.endpoint)
        assert response.status_code == 200
        assert response.data == []
