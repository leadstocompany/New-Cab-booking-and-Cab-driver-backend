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
    suggetions_text=models.CharField(max_length=500, null=True, blank=True)
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


class DriverFeedbackPage(models.Model):
    title=models.CharField(max_length=500)
    description=models.CharField(max_length=500, null=True, blank=True)
    active=models.BooleanField(default=True)
    def __str__(self):
        return self.title
    

class VehiclePhotoPage(models.Model):
    field_name=models.CharField(max_length=500, unique=True)
    active=models.BooleanField(default=True)
    def __str__(self):
        return self.field_name


class City(BaseModel):
    city_name=models.CharField(max_length=500, unique=True)
    def __str__(self):
        return self.city_name


from django.db import models

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255)
    html_content = models.TextField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"
    
    def save(self, *args, **kwargs):
        # If this template is being set as active, deactivate all other templates with the same name
        if self.is_active:
            EmailTemplate.objects.filter(name=self.name, is_active=True).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)
