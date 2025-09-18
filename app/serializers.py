from rest_framework import serializers
from .models import LogJob

class LogJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogJob
        fields = ["id", "created_at", "filename", "size_bytes", "status", "parsed_preview", "llm_summary", "llm_cost_usd", "error_msg"]
        read_only_fields = ["id", "created_at", "status", "parsed_preview", "llm_summary", "llm_cost_usd", "error_msg"]

class LogUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
