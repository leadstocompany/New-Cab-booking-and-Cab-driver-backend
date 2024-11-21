from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path, path
# from . import consumers
from JLP_MyRide import consumers
websocket_urlpatterns = [
  
    re_path(r'ws/admin/sos/(?P<user_id>\d+)/$', consumers.SOSConsumer.as_asgi()),
    re_path(r'ws/payment-notify/(?P<user_id>\d+)/$', consumers.PaymenNotificationConsumer.as_asgi()),
    re_path(r'ws/driver/(?P<user_id>\d+)/$',consumers.DriverConsumer.as_asgi()), 
    re_path(r'ws/customer/(?P<user_id>\d+)/$', consumers.CustomerConsumer.as_asgi()),
    re_path(r'ws/booked-ride-driver-location-tracker/(?P<ride_id>\d+)/(?P<driver_id>\d+)/(?P<passenger_id>\d+)/$', consumers.BookedRideDriverTrackerConsumer.as_asgi()),
]




