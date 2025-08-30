# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ConsultationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'consultation_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']
        if message_type == 'offer':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_offer',
                    'sdp': data['sdp'],
                }
            )
        elif message_type == 'answer':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_answer',
                    'sdp': data['sdp'],
                }
            )
        elif message_type == 'ice':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'ice_candidate',
                    'candidate': data['candidate'],
                }
            )

    async def video_offer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'sdp': event['sdp'],
        }))

    async def video_answer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'sdp': event['sdp'],
        }))

    async def ice_candidate(self, event):
        await self.send(text_data=json.dumps({
            'type': 'ice',
            'candidate': event['candidate'],
        }))
