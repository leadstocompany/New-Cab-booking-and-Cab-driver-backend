from rest_framework import serializers
from .models import Payment  # Import your Payment model

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        # fields = '__all__'  # Or list the specific fields you want to include
        fields = ['id', 'trip', 'driver', 'passenger', 'amount', 'currency', 'payment_type', 'payment_id', 'payment_status']