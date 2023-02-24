from django.urls import path
from .WmConsumers import waitingRoomRequest,chatRoomRequest
wm_patterns=[
    path("ws/waitingroom/",waitingRoomRequest.as_asgi()),
    path("ws/chatroom/",chatRoomRequest.as_asgi()),
] 