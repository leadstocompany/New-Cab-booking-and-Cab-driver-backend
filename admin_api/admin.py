from django.contrib import admin

from admin_api.models import *

# Register your models here.


admin.site.register(UserDocumentField)
admin.site.register(VehicleCertificateField)
admin.site.register(FeedbackSetting)
admin.site.register(DriverFeedbackPage)
admin.site.register(VehiclePhotoPage)
admin.site.register(City)