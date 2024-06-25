from django.db import models
from accounts.models import User
from utility.model import BaseModel
from django.utils.crypto import get_random_string
# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    room = models.ForeignKey('O2ORoom', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)

def generate_room_name():
    while 1:
        room = get_random_string(18).lower()
        if room not in list(O2ORoom.objects.values_list('room', flat=True)):
            print(room)
            return room
            break
        else:
            continue

class O2ORoom(BaseModel):
    sender_receiver = models.JSONField()
    room = models.CharField(max_length=18, default=generate_room_name)

    def __str__(self):
        return self.room
    