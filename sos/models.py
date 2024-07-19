from django.db import models

from accounts.models import User
from trips.models import Trip
# Create your models here.

class SOSHelpRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip=models.ForeignKey(Trip,on_delete=models.CASCADE)
    message = models.TextField()
    location=models.CharField(max_length=2000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f'HelpRequest from {self.user.username}'


