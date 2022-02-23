"""
ASGI config for DiscusionForum project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from chatRoom.routing import wm_patterns
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DiscusionForum.settings')
django.setup()
application = ProtocolTypeRouter({
    "http":get_asgi_application(),
    "websocket":AuthMiddlewareStack(URLRouter(wm_patterns))
})


