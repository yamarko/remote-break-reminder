from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import BreakInterval, BreakLog
from .serializers import BreakIntervalSerializer, BreakLogSerializer


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
    logs = BreakLog.objects.filter(user=request.user).order_by('-triggered_at')[:5]
    return render(request, 'dashboard.html', {'break_logs': logs})
