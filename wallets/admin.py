from django.contrib import admin

# Register your models here.

from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance']  # Display fields in the admin list view
    search_fields = ['user__phone']  # Enable searching by user's username
    # readonly_fields = ['balance']  # Make balance read-only in the admin interface
    list_filter = ['user']  # Add filtering options in the sidebar

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount', 'date']  # Display key fields
    search_fields = ['user__phone']  # Search by user's username
    list_filter = ['transaction_type', 'date']  # Add filtering for transaction type and date
    # date_hierarchy = 'date'  # Add a date hierarchy to the admin interface
