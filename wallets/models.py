from django.db import models
from accounts.models import User
from django.utils import timezone
# Create your models here.
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.localtime(timezone.now()))

    def __str__(self):
        return f'{self.user.phone} - Balance: {self.balance}'

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
        ('EXPENSE', 'Expense'),
        ('INCOME', 'Income'),
    ]
    
    TRANSACTION_MODE = [
        ('WALLETS', 'Wallets'),
        ('HANDCASH', 'HandCash'),
        ('STRIPEPAY', 'StripePay'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='transaction_sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='transaction_receiver')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=80, choices=TRANSACTION_TYPES)
    transaction_mode = models.CharField(max_length=80, choices=TRANSACTION_MODE, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    remark = models.CharField(max_length=1000, null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.phone} - {self.transaction_type} - {self.amount}'

