from django.contrib import admin
from .models import SubscriptionPlan, Subscriptions, Subscription_Logs

# Register your models here.



@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_name', 'vehicle_class', 'days', 'price', 'discount', 'original_price', 'is_active', 'created_at', 'updated_at')
    list_filter = ('vehicle_class', 'is_active')
    search_fields = ('plan_name', 'vehicle_class__name')


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('driver', 'plan', 'pay_amount', 'subcribe_date', 'expire_date', 'payment_status', 'is_active', 'payment_id')
    list_filter = ('payment_status', 'is_active', 'subcribe_date')
    search_fields = ('driver__phone', 'plan__plan_name', 'payment_id')
    date_hierarchy = 'subcribe_date'


@admin.register(Subscription_Logs)
class SubscriptionLogsAdmin(admin.ModelAdmin):
    list_display = ('driver', 'plan', 'pay_amount', 'subcribe_date', 'expire_date', 'payment_status', 'is_active', "payment_id")
    list_filter = ('payment_status', 'is_active', 'subcribe_date')
    search_fields = ('driver__phone', 'plan__plan_name', 'payment_id')
    date_hierarchy = 'subcribe_date'




