from django.db import models

class LogJob(models.Model):
    STATUS = [
        ("PENDING", "PENDING"),
        ("DONE", "DONE"),
        ("ERROR", "ERROR"),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    size_bytes = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS, default="PENDING")

    #~ Let's save some artifacts for debug/portfolio
    parsed_preview = models.JSONField(null=True, blank=True)
    llm_summary = models.TextField(null=True, blank=True)      # summary of the LLM
    llm_cost_usd = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    error_msg = models.TextField(null=True, blank=True)
