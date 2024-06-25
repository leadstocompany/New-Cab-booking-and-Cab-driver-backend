from django.contrib import admin
from cabs.models import *
# Register your models here.

admin.site.register(Vehicle)
admin.site.register(VehicleMaker)
admin.site.register(VehicleModel)
admin.site.register(CabType)
admin.site.register(CabClass)

