from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import SOSHelpRequest
from .serializers import SOSHelpRequestSerializer

@shared_task
def send_sos_notification(sos_request_id):
    sos_request = SOSHelpRequest.objects.get(id=sos_request_id)
    channel_layer = get_channel_layer()
    message = SOSHelpRequestSerializer(sos_request).data

    async_to_sync(channel_layer.group_send)(
        "admins",
        {
            "type": "send_sos",
            "message": message,
        }
    )
