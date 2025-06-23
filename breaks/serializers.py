from rest_framework import serializers
from .models import BreakInterval


class BreakIntervalSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = BreakInterval
        fields = ['id', 'user', 'interval_minutes', 'created_at', 'updated_at']
