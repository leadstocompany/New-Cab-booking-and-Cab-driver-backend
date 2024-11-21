from django.contrib import admin
from trips.models import *
# Register your models here.


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'driver', 'status', 'source', 'destination', 'scheduled_datetime', 'created_at' , 'payment_type')
    search_fields = ('customer__phone', 'driver__phone', 'source', 'destination')
    list_filter = ('status', 'ride_type', 'scheduled_datetime')
    readonly_fields = ('otp', 'order_id')


# admin.site.register(Trip)

admin.site.register(TripRating)

# admin.site.register(DriverPricingRatio)
