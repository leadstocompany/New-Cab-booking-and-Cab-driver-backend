from django.contrib import admin
from cabs.models import *
# Register your models here.

# admin.site.register(Vehicle)
admin.site.register(VehicleMaker)
# admin.site.register(VehicleModel)
admin.site.register(CabType)
admin.site.register(CabClass)
admin.site.register(CabBookingPrice)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('driver', 'maker', 'model', 'number_plate', 'cab_type', 'cab_class', 'is_approved')
    list_filter = ('is_approved', 'cab_type', 'cab_class')
    search_fields = ('number_plate', 'driver__phone')



@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ('model', 'maker', 'cabtype', 'cabclass')  # Fields to display in admin list view
    search_fields = ('model',)  # Searchable fields
