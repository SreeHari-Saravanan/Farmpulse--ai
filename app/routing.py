from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path('ws://127.0.0.1:8000/ws/consultation/farmer_vet_room/', consumers.ConsultationConsumer.as_asgi()),
]
