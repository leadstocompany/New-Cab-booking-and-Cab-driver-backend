from django.db import models

from accounts.models import User
from trips.models import Trip
from django.utils import timezone

from utility.model import BaseModel
# Create your models here.


class SOSMessage(BaseModel):
    message = models.CharField(max_length=255)

    def __str__(self):
        return self.message

class SOSHelpRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip=models.ForeignKey(Trip,on_delete=models.CASCADE)
    message = models.TextField()
    location=models.TextField(null=True, blank=True)
    last_latitude = models.CharField(max_length=50, null=True, blank=True)
    last_longitude = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.localtime(timezone.now()))
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f'HelpRequest from {self.user.username}'
