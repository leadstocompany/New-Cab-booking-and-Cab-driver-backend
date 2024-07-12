"""
ASGI config for JLP_MyRide project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "JLP_MyRide.settings") 
django.setup()

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from . import routing


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})


# format second
# import os
# import django
# from channels.routing import get_default_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JLP_MyRide.settings')
# django.setup()
# application = get_default_application()


# format 3rd 
# asgi.py

# import os
# import django
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from django.core.asgi import get_asgi_application
# from django.urls import path
# from your_app_name.consumers import DriverConsumer, CustomerConsumer

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
# django.setup()

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter([
#             path("ws/driver/", DriverConsumer),
#             path("ws/customer/", CustomerConsumer),
#         ])
#     ),
# })

