from django.contrib import admin
from .models import WalletTransaction


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('user__email', 'stripe_payment_intent_id', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('user', 'transaction_type', 'amount', 'status')
        }),
        ('Stripe Info', {
            'fields': ('stripe_payment_intent_id',)
        }),
        ('Additional Info', {
            'fields': ('description', 'created_at', 'updated_at')
        }),
    )
