from rest_framework import serializers
from decimal import Decimal
from .models import WalletTransaction


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ('id', 'transaction_type', 'amount', 'status', 'description', 'created_at')
        read_only_fields = ('id', 'created_at')


class TopUpSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('1.00'))