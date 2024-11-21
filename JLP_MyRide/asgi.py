"""
ASGI config for JLP_MyRide project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from . import routing


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "JLP_MyRide.settings") 
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})


# # asgi.py
# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.sessions import SessionMiddlewareStack
# from .middleware import TokenAuthMiddleware  # Import your custom middleware
# from . import routing # Adjust to your app's name

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JLP_MyRide.settings')

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": SessionMiddlewareStack(
#         TokenAuthMiddleware(
#             URLRouter(
#                 routing.websocket_urlpatterns
#             )
#         )
#     ),
# })


