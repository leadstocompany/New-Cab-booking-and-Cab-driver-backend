from django.db import models
from accounts.models import Customer
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
# Create your models here.


    
class ReferralReward(models.Model):
    title = models.CharField(max_length=2000, null=True, blank=True)
    referrer_reward_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=50.00, help_text="Reward amount for the inviter (referrer)."
    )
    referred_reward_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=25.00, help_text="Reward amount for the invited (referred) customer."
    )

    class Meta:
        db_table = 'referral_reward'
    
    def __str__(self):
        return f"Referral Reward: {self.referrer_reward_amount} for inviter, {self.referred_reward_amount} for invited"

class CustomerReferral(models.Model):
    referrer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='referreds')
    referred = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='referrers')
    referrer_reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    referred_reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        unique_together = (('referrer', 'referred'),)
        db_table = 'customer_referral'  # Defines the table name in the database
        verbose_name = 'Customer Referral'  # Human-readable name for the model
        verbose_name_plural = 'Customer Referrals'  # Human-readable plural name

    def __str__(self):
        return f'{self.referrer} => {self.referred}'

    def save(self, *args, **kwargs):
        # Apply dynamic reward if not already set
        self.full_clean()
        return super(CustomerReferral, self).save(*args, **kwargs)