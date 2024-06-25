from django.db import models
from accounts.models import User
# Create your models here.
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.user.username} - Balance: {self.balance}'

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=18, choices=TRANSACTION_TYPES)
    date = models.DateTimeField(auto_now_add=True)
    remake=models.CharField(max_length=100,null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.transaction_type} - {self.amount}'
