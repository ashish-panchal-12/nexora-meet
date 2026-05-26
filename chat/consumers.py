import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.meeting_id     = self.scope['url_route']['kwargs']['meeting_id']
        self.room_group_name = f'chat_{self.meeting_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Announce user joined
        user = self.scope['user']
        if user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':     'system_message',
                    'message':  f'{user.get_full_name() or user.username} joined the meeting',
                }
            )

    async def disconnect(self, close_code):
        user = self.scope['user']
        if user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':    'system_message',
                    'message': f'{user.get_full_name() or user.username} left the meeting',
                }
            )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data     = json.loads(text_data)
        message  = data.get('message', '').strip()
        username = data.get('username', 'Anonymous')

        if not message:
            return

        now = timezone.localtime(timezone.now())
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':      'chat_message',
                'message':   message,
                'username':  username,
                'timestamp': now.strftime('%I:%M %p'),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type':      'chat',
            'message':   event['message'],
            'username':  event['username'],
            'timestamp': event['timestamp'],
        }))

    async def system_message(self, event):
        await self.send(text_data=json.dumps({
            'type':    'system',
            'message': event['message'],
        }))
