from django.contrib import admin

from .models import BreakInterval, BreakLog

admin.site.register(BreakInterval)
admin.site.register(BreakLog)
