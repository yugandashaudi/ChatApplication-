from django.urls import path

from .consumers import *

websocket_urlpatterns = [
    path('ws/chat/<conversation_name>/', ChatConsumer.as_asgi()),
    path('ws/notification/',NotificationConsumer.as_asgi())
]