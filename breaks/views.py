from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import BreakInterval, BreakLog
from .serializers import BreakIntervalSerializer, BreakLogSerializer

from datetime import timedelta


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponse("Login successful!")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return HttpResponse("Logout successful!")


class BreakIntervalViewSet(viewsets.ModelViewSet):
    serializer_class = BreakIntervalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BreakInterval.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BreakLoglViewSet(viewsets.ModelViewSet):
    serializer_class = BreakLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BreakLog.objects.filter(user=self.request.user).order_by('-triggered_at')


def dashboard_view(request):
    logs_qs = BreakLog.objects.filter(user=request.user)
    logs = logs_qs.order_by('-triggered_at')[:5]
    total_breaks = logs_qs.count()

    interval = BreakInterval.objects.filter(user=request.user).first()
    last_break = logs.first() if interval else None

    if interval and last_break:
        next_break = last_break.triggered_at + timedelta(minutes=interval.interval_minutes)
    else:
        next_break = None

    context = {
        'break_logs': logs,
        'total_breaks': total_breaks,
        'next_break': next_break,
        'username': request.user.get_full_name() or request.user.username,
    }

    return render(request, 'dashboard.html', context)
