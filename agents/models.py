import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from decimal import Decimal


class AgentCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name or emoji")
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'Agent Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Agent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=255, help_text="Brief description for cards")
    category = models.ForeignKey(AgentCategory, on_delete=models.CASCADE, related_name='agents')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in AED")
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name or emoji")
    
    # Dynamic form configuration
    form_schema = models.JSONField(
        default=dict,
        help_text="JSON schema defining the form fields for this agent"
    )
    
    # n8n integration
    n8n_webhook_url = models.URLField(help_text="n8n webhook URL for this agent")
    
    # Response configuration
    result_format = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configuration for formatting the response from n8n"
    )
    
    # Status and metadata
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-usage_count', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def increment_usage(self):
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class AgentExecution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agent_executions')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='executions')
    
    # Execution data
    input_data = models.JSONField(help_text="Form data submitted by user")
    output_data = models.JSONField(null=True, blank=True, help_text="Response from n8n workflow")
    
    # Billing
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.agent.name} - {self.status}"
