from django.db import models
from utility.model import BaseModel
# Create your models here.

class UserDocumentField(models.Model):
    field_name=models.CharField(max_length=500, unique=True)
    textfield=models.BooleanField(default=False)
    filefield=models.BooleanField(default=True)
    front=models.BooleanField(default=True)
    back=models.BooleanField(default=False)
    active=models.BooleanField(default=True)
    def __str__(self):
        return self.field_name


class VehicleCertificateField(models.Model):
    field_name=models.CharField(max_length=500, unique=True)
    active=models.BooleanField(default=True)
    def __str__(self):
        return self.field_name
    


class FeedbackSetting(models.Model):
    title=models.CharField(max_length=500)
    sub_title=models.CharField(max_length=500, null=True, blank=True)
    active=models.BooleanField(default=True)
    def __str__(self):
        return self.title


