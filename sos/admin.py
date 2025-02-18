from django.contrib import admin

from sos.models import SOSMessage, SOSHelpRequest

# Register your models here.

admin.site.register(SOSMessage)
admin.site.register(SOSHelpRequest)
