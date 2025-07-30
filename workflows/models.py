import uuid
from django.db import models
from django.conf import settings
from decimal import Decimal


class WorkflowUsage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workflow_usage')
    workflow_name = models.CharField(max_length=255)
    workflow_url = models.URLField()
    fee_charged = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.10'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.workflow_name} - ${self.fee_charged}"
