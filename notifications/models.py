from cloudinary.models import CloudinaryField
from django.db import models

from utility.model import CloudinaryBaseModel, BaseModel


class DriverNotification(CloudinaryBaseModel):
    banner = models.CharField(null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return str(self.title)

    def get_cloudinary_folder(self, field_name):
        return f"notifications/{self.title}"

    def get_file_fields(self):
        return ["banner"]

    def send_notification_to_drivers(self):
        from notifications.tasks import send_driver_notifications

        send_driver_notifications.delay(self.id)


class NotificationTemplate(models.Model):
    TYPE_CHOICES = [
        ('TripBillGenerate', 'Trip Bill Generate'),
        ('TripPaymentComplete', 'Trip Payment Complete'),
        ('TripBookingRequest', 'Trip Booking Request'),
        ('TripAccepted', 'Trip Accepted'),
        ('TripCancelled', 'Trip Cancelled'),
        ('TripStart', 'Trip Start'),
        ('TripScheduled', 'Trip Scheduled'),
        ('TripComplete', 'Trip Complete'),
        ('TripDriverArrived', 'Trip Driver Arrived'),
    ]

    name = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
