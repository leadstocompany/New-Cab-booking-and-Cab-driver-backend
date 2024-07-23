# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.layers import get_channel_layer
# from channels.db import database_sync_to_async
# from chat.models import Message, O2ORoom
# import ast
# from chat.serializers import MessageSerializer

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room = self.scope['url_route']['kwargs']['-room']
#         self.room_group_name = f'chat_{self.room}'

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         if await self.checK_room(self.room):
#             await self.accept()
#         else:
#             await self.close()
    
#     @database_sync_to_async
#     def checK_room(self, room):
#         if 1:
#             self.room_id = 1
#         return qs.exists()

#     async def disconnect(self, close_code):
#         print(self.room_group_name,
#             self.channel_name)
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     def create_message(self, sender, receiver, message):
#         message_obj = Message(
#             room_id=self.room_id,
#             sender_id=sender,
#             receiver_id=receiver,
#             message=message
#         )
#         return message_obj

#     async def receive(self, text_data):
#         try:
#             data = ast.literal_eval(text_data.replace("\n" , "").strip())
#             sender = data.get('sender')
#             receiver = data.get('receiver')
#             message = data.get('message')

#             message_obj = await self.create_message(sender=sender, receiver=receiver,
#                                                     message=message)

#             message_data = MessageSerializer(message_obj).data
#             message_data.update({'status':1})
            
#         except Exception as e:
#             message_data = {"error":str(e), "status":0}
            
#         message_data.update({'type': 'chat_message'})
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             message_data
#         )

#     async def chat_message(self, event):
#         await self.send(text_data=json.dumps(event))


# class TripConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room = self.scope['url_route']['kwargs']['room']
#         self.room_group_name = f'trip-notify_{self.room}'

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.close()
    
#     async def disconnect(self, close_code):
#         print(self.room_group_name,
#             self.channel_name)
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )


#     async def receive(self, text_data):
#         # try:
#         data = ast.literal_eval(text_data.replace("\n" , "").strip())
            
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             data
#         )
        
#     async def trip_notify_message(self, event):
#         await self.send(text_data=json.dumps(event))

# class PaymentConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room = self.scope['url_route']['kwargs']['room']
#         self.room_group_name = f'trip-notify_{self.room}'

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.close()
    
#     async def disconnect(self, close_code):
#         print(self.room_group_name,
#             self.channel_name)
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         # try:
#         data = ast.literal_eval(text_data.replace("\n" , "").strip())
            
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             data
#         )
    
#     async def gpay_notify_message(self, event):
#         await self.send(text_data=json.dumps(event))


import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DriverConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["user"].id
        self.group_name = f'driver_{self.user_id}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_trip_request(self, event):
        await self.send(text_data=json.dumps(event))

    async def send_trip_cancelled(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def trip_completed(self, event):
        message = event['message']
        trip_id = event['trip_id']

        await self.send(text_data=json.dumps({
            'type': 'trip.completed',
            'message': message,
            'trip_id': trip_id
        }))

class CustomerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["user"].id
        self.group_name = f'customer_{self.user_id}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_trip_booked(self, event):
        await self.send(text_data=json.dumps(event))

    async def send_trip_cancelled(self, event):
        await self.send(text_data=json.dumps(event))

    async def trip_started(self, event):
        await self.send(text_data=json.dumps(event))
    

    async def trip_completed(self, event):
        message = event['message']
        trip_id = event['trip_id']

        await self.send(text_data=json.dumps({
            'type': 'trip.completed',
            'message': message,
            'trip_id': trip_id
        }))




class SOSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_staff:
            await self.channel_layer.group_add("admins", self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.scope["user"].is_staff:
            await self.channel_layer.group_discard("admins", self.channel_name)

    async def receive(self, text_data):
        pass  # No need to handle incoming messages

    async def send_sos(self, event):
        await self.send(text_data=json.dumps(event["message"]))



class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = f"user_{self.user.id}"

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from room group
    async def send_real_time_notification(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
    async def send_payment_request_notification(self, event):
        # message = event['message']
        # trip_id = event['trip_id']
        # source=event['source'],
        # destination=event['destination'],
        # time =event['time'],
        # distance=event['distance'],
        # waiting_charge=event['waiting_charge'],
        # waiting_time=event['waiting_time'],
        # total_fare=event['total_fare']

        # await self.send(text_data=json.dumps({
        #     'type': 'trip.completed',
        #     'message': message,
        #     'trip_id': trip_id
        # }))
        await self.send(text_data=json.dumps(event))
