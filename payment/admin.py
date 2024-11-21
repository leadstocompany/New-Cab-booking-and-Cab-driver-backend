from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Bill_Payment

@admin.register(Bill_Payment)
class BillPaymentAdmin(admin.ModelAdmin):
    list_display = ('trip', 'driver', 'passenger','payment_id', 'amount', 'currency', 'payment_type', 'payment_status')
    search_fields = ('trip__id', 'driver__name', 'passenger__name', 'payment_status')
    list_filter = ('payment_status', 'currency')