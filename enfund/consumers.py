import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "enfund.settings")
django.setup()  # Init
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from enfund_view.models import Message
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles new WebSocket connections and sends recent messages"""
        await self.accept()

        # Fetch last 10 messages from the database
        messages = await self.get_last_messages()

        # Send messages to the client
        await self.send(text_data=json.dumps({
            "messages": messages
        }))

    async def receive(self, text_data):
        """Handles messages received from the client"""
        data = json.loads(text_data)
        username = data.get("username", "Guest")
        message_text = data.get("message", "")

        # Save message to database
        message = await self.save_message(username, message_text)

        # Send message to the WebSocket client
        await self.send(text_data=json.dumps({
            "message": {
                "id": message.id,
                "username": message.username,
                "text": message.text,
                "timestamp": str(message.timestamp)
            }
        }))

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection"""
        pass

    @sync_to_async
    def get_last_messages(self):
        messages = Message.objects.all()
        return [{"id": msg.id, "username": msg.username, "text": msg.text, "timestamp": str(msg.timestamp)} for msg in messages]

    # Save message asynchronously
    @sync_to_async
    def save_message(self, username, text):
        return Message.objects.create(username=username, text=text)
