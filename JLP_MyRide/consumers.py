import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from chat.models import Message, O2ORoom
import ast
from chat.serializers import MessageSerializer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room = self.scope['url_route']['kwargs']['-room']
        self.room_group_name = f'chat_{self.room}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        if await self.checK_room(self.room):
            await self.accept()
        else:
            await self.close()
    
    @database_sync_to_async
    def checK_room(self, room):
        if 1:
            self.room_id = 1
        return qs.exists()

    async def disconnect(self, close_code):
        print(self.room_group_name,
            self.channel_name)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    def create_message(self, sender, receiver, message):
        message_obj = Message(
            room_id=self.room_id,
            sender_id=sender,
            receiver_id=receiver,
            message=message
        )
        return message_obj

    async def receive(self, text_data):
        try:
            data = ast.literal_eval(text_data.replace("\n" , "").strip())
            sender = data.get('sender')
            receiver = data.get('receiver')
            message = data.get('message')

            message_obj = await self.create_message(sender=sender, receiver=receiver,
                                                    message=message)

            message_data = MessageSerializer(message_obj).data
            message_data.update({'status':1})
            
        except Exception as e:
            message_data = {"error":str(e), "status":0}
            
        message_data.update({'type': 'chat_message'})
        await self.channel_layer.group_send(
            self.room_group_name,
            message_data
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))


class TripConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room = self.scope['url_route']['kwargs']['room']
        self.room_group_name = f'trip-notify_{self.room}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.close()
    
    async def disconnect(self, close_code):
        print(self.room_group_name,
            self.channel_name)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data):
        # try:
        data = ast.literal_eval(text_data.replace("\n" , "").strip())
            
        await self.channel_layer.group_send(
            self.room_group_name,
            data
        )
        
    async def trip_notify_message(self, event):
        await self.send(text_data=json.dumps(event))

class PaymentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room = self.scope['url_route']['kwargs']['room']
        self.room_group_name = f'trip-notify_{self.room}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.close()
    
    async def disconnect(self, close_code):
        print(self.room_group_name,
            self.channel_name)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # try:
        data = ast.literal_eval(text_data.replace("\n" , "").strip())
            
        await self.channel_layer.group_send(
            self.room_group_name,
            data
        )
    
    async def gpay_notify_message(self, event):
        await self.send(text_data=json.dumps(event))