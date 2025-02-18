from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomerReferral, ReferralReward

@admin.register(CustomerReferral)
class CustomerReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred', 'referrer_reward_amount', 'referred_reward_amount')
    search_fields = ('referrer__name', 'referred__name')  # Assuming 'name' is a field in Customer model
    list_filter = ('referrer_reward_amount', 'referred_reward_amount')

admin.site.register(ReferralReward)