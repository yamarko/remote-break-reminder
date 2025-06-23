import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse
from rest_framework.test import APIClient
from .models import BreakInterval


@pytest.fixture
def user(db):
    return User.objects.create_user(username='test_user', password='pass123')


@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)

    return client


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


@pytest.mark.django_db
class TestBreakIntervalAPI:

    def test_get_interval(self, authenticated_client, user):
        BreakInterval.objects.create(user=user)

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

    def test_partial_update_interval(self, authenticated_client, user):
        BreakInterval.objects.create(user=user)
        partial_data = {"interval_minutes": 75}

        response = authenticated_client.patch(
            reverse("break-interval-detail", kwargs={"pk": user.breakinterval.pk}),
            partial_data,
        )

        assert response.status_code == 200

        user.breakinterval.refresh_from_db()
        assert user.breakinterval.interval_minutes == 75

    def test_delete_interval(self, authenticated_client, user):
        BreakInterval.objects.create(user=user)

        response = authenticated_client.delete(
            reverse("break-interval-detail", kwargs={"pk": user.breakinterval.pk})
        )

        assert response.status_code == 204
        assert BreakInterval.objects.count() == 0
