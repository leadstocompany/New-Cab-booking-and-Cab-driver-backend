from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'chat/(?P<room>\w+)', consumers.ChatConsumer.as_asgi()),
    re_path(r'trip-notify/(?P<room>\w+)', consumers.TripConsumer.as_asgi()),
    re_path(r'payment-notify/(?P<room>\w+)', consumers.PaymentConsumer.as_asgi())
]
