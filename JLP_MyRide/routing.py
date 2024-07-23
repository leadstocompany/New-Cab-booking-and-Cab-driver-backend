from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path, path
# from . import consumers
from JLP_MyRide.consumers import DriverConsumer, CustomerConsumer, SOSConsumer, NotificationConsumer

websocket_urlpatterns = [
    # re_path(r'chat/(?P<room>\w+)', consumers.ChatConsumer.as_asgi()),
    # re_path(r'trip-notify/(?P<room>\w+)', consumers.TripConsumer.as_asgi()),
    # re_path(r'payment-notify/(?P<room>\w+)', consumers.PaymentConsumer.as_asgi())
    path("ws/driver/", DriverConsumer.as_asgi()),
    path("ws/customer/", CustomerConsumer.as_asgi()),
    re_path(r'ws/sos/$', SOSConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]




# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from django.core.asgi import get_asgi_application
# from django.urls import path
# from your_app_name.consumers import DriverConsumer, CustomerConsumer

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter([
#             path("ws/driver/", DriverConsumer),
#             path("ws/customer/", CustomerConsumer),
#         ])
#     ),
# })