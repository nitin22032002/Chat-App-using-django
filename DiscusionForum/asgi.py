import os
import django
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from chatRoom.routing import wm_patterns
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DiscusionForum.settings')
application = ProtocolTypeRouter({
    "websocket":AuthMiddlewareStack(URLRouter(wm_patterns)),
    "http":get_asgi_application()
})