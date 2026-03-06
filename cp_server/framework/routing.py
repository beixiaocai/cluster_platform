from django.urls import re_path
from app.consumers import ClusterConsumer

websocket_urlpatterns = [
    re_path(r'ws/cluster/$', ClusterConsumer.as_asgi()),
]
