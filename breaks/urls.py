from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'break-intervals', views.BreakIntervalViewSet, basename='break-interval')
router.register(r'break-logs', views.BreakLoglViewSet, basename='break-log')

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/', include(router.urls)),
]
