from django.contrib import admin
from .models import WorkflowUsage


@admin.register(WorkflowUsage)
class WorkflowUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'workflow_name', 'fee_charged', 'status', 'created_at')
    list_filter = ('status', 'workflow_name', 'created_at')
    search_fields = ('user__email', 'workflow_name', 'workflow_url')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Workflow Info', {
            'fields': ('user', 'workflow_name', 'workflow_url', 'fee_charged', 'status')
        }),
        ('Request Data', {
            'fields': ('request_data',),
            'classes': ('collapse',)
        }),
        ('Response Data', {
            'fields': ('response_data', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
