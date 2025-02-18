from django.contrib import admin

from support.models import CustomerSupport, DriverSupport

# Register your models here.
admin.site.register(CustomerSupport)
admin.site.register(DriverSupport)