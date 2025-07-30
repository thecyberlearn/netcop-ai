from django.contrib import admin
from django.utils.html import format_html
from .models import AgentCategory, Agent, AgentExecution


@admin.register(AgentCategory)
class AgentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'agent_count', 'is_active', 'sort_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('sort_order', 'name')

    def agent_count(self, obj):
        return obj.agents.filter(is_active=True).count()
    agent_count.short_description = 'Active Agents'


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'usage_count', 'is_active', 'is_featured', 'created_at')
    list_filter = ('category', 'is_active', 'is_featured', 'created_at')
    search_fields = ('name', 'description', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-is_featured', '-usage_count', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'price', 'icon')
        }),
        ('Descriptions', {
            'fields': ('short_description', 'description')
        }),
        ('Form Configuration', {
            'fields': ('form_schema',),
            'classes': ('collapse',),
            'description': 'JSON schema defining the form fields for this agent'
        }),
        ('n8n Integration', {
            'fields': ('n8n_webhook_url', 'result_format'),
            'classes': ('collapse',)
        }),
        ('Status & Settings', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('usage_count',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('usage_count',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add help text for form_schema field
        if 'form_schema' in form.base_fields:
            form.base_fields['form_schema'].help_text = format_html('''
                <p>JSON schema example:</p>
                <pre>{
  "fields": [
    {
      "name": "description",
      "type": "textarea", 
      "label": "Content Description",
      "required": true,
      "placeholder": "Describe what you want to generate..."
    },
    {
      "name": "language",
      "type": "select",
      "label": "Language", 
      "options": ["English", "Arabic"],
      "required": true
    }
  ]
}</pre>
            ''')
        return form


@admin.register(AgentExecution)
class AgentExecutionAdmin(admin.ModelAdmin):
    list_display = ('user', 'agent', 'status', 'price_paid', 'created_at', 'completed_at')
    list_filter = ('status', 'agent', 'created_at')
    search_fields = ('user__email', 'agent__name')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Execution Info', {
            'fields': ('user', 'agent', 'status', 'price_paid')
        }),
        ('Input Data', {
            'fields': ('input_data',),
            'classes': ('collapse',)
        }),
        ('Output Data', {
            'fields': ('output_data', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return self.readonly_fields + ('user', 'agent', 'price_paid')
        return self.readonly_fields
