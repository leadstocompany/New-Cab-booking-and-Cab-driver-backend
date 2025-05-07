from django.db import models
from utility.model import BaseModel
from django.template import Template, Context

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
    EMAIL_TYPES = (
        ("TripBillGenerate", "Generate Tripm Bill"),
        ("AccountActivation", "Activate Account"),
        ("AccountDeactivation", "Deactivate Account"),
    )
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=EMAIL_TYPES)
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
        # If this template is being set as active, deactivate all other templates with the same type
        TYPES_ = ["TripBillGenerate", "AccountActivation", "AccountDeactivation"]
        EXCLUDE_TYPES_ = []
        for type_ in TYPES_:
            if self.type != type_:
                EXCLUDE_TYPES_.append(type_)

        if self.is_active:
            EmailTemplate.objects.filter(type=self.type, is_active=True).exclude(id=self.id, type__in=EXCLUDE_TYPES_).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_template(cls, email_type):
        """Get the active template for a specific email type"""
        try:
            return cls.objects.get(type=email_type, is_active=True)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def render_template(cls, email_type, context_data):
        """Render a template with the given context data"""
        template = cls.get_active_template(email_type)
        if not template:
            return None, None
        
        subject = Template(template.subject)
        content = Template(template.html_content)
        context_ = Context(context_data)
        
        return subject.render(context_), content.render(context_)
