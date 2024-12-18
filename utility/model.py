from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)  # Stores datetime in UTC
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract=True
