import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
import asyncio
from datetime import datetime

from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist





class DriverConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'driver_{user_id}'
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
        await self.send(text_data=json.dumps(event))
    async def send_trip_schedule_notification(self, event):
        await self.send(text_data=json.dumps(event))

    

class CustomerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'customer_{user_id}'
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
        await self.send(text_data=json.dumps(event))
    async def send_trip_schedule_notification(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def arrived_at_pickup(self, event):
        await self.send(text_data=json.dumps(event))





class SOSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from accounts.models import User
        user_id = self.scope['url_route']['kwargs']['user_id']
        user=User.objects.get(id=user_id)
        if user.is_staff:
            await self.channel_layer.group_add("admins", self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        from accounts.models import User
        self.user_id = self.scope["user"].id
        user=User.objects.get(id=self.user_id)
        if user.is_staff:
            await self.channel_layer.group_discard("admins", self.channel_name)

    async def receive(self, text_data):
        pass  # No need to handle incoming messages

    async def send_sos(self, event):
        await self.send(text_data=json.dumps(event["message"]))


class PaymenNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"payment_{user_id}"

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

    async def send_trip_bille_notification(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def send_trip_payment_complete(self, event):
        await self.send(text_data=json.dumps(event))




class BookedRideDriverTrackerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Extract parameters from the URL
            self.ride_id = self.scope['url_route']['kwargs']['ride_id']
            self.driver_id = self.scope['url_route']['kwargs']['driver_id']
            self.passenger_id = self.scope['url_route']['kwargs']['passenger_id']

            # Fetch the trip asynchronously
            trip = await self.get_trip()
            if trip == True:
                await self.accept()
                while True:
                    await self.send_driver_location()
                    await asyncio.sleep(5)  # 10-second interval
            else:
                await self.close()

        except Exception as e:
            await self.close()

    @database_sync_to_async
    def get_trip(self):
        # Fetch the driver's location from the database
        from trips.models import Trip
        trip = Trip.objects.get(id=self.ride_id)
        if (trip.driver.id == int(self.driver_id) and trip.customer.id == int(self.passenger_id)) and (trip.status in ['ACCEPTED', 'BOOKED', 'ON_TRIP']):
            return True
        else:
            return False
    async def send_driver_location(self):
            location_data = await self.get_driver_location()
            await self.send(text_data=json.dumps({
                'driver_id':location_data['driver_id'],
                'driver_name':location_data['driver_name'],
                'driver_phone':location_data['driver_phone'],
                'current_latitude': location_data['current_latitude'],
                'current_longitude': location_data['current_longitude'],
                'timestamp':location_data['timestamp']
            }))

    @database_sync_to_async
    def get_driver_location(self):
        # Fetch the driver's location from the database
        from accounts.models import CurrentLocation
        driver = CurrentLocation.objects.filter(user__id=self.driver_id).first()
        return {
            'driver_id':driver.user.id,
            'driver_name': driver.user.first_name + " " + driver.user.last_name,
            'driver_phone':driver.user.phone,
            'current_latitude': driver.current_latitude,
            'current_longitude': driver.current_longitude,
            'timestamp':str(driver.timestamp)
        }
    
class DriverLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.driver_id = self.scope['url_route']['kwargs']['driver_id']
        self.group_name = f'driver_location_{self.driver_id}'
        
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

    async def receive(self, text_data):
        location_data = json.loads(text_data)
        
        # Save location to database
        await self.update_driver_location(
            latitude=location_data.get('latitude'),
            longitude=location_data.get('longitude')
        )

        # Broadcast location update
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'location_update',
                'latitude': location_data.get('latitude'),
                'longitude': location_data.get('longitude'),
                'timestamp': str(datetime.now())
            }
        )

    async def location_update(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def update_driver_location(self, latitude, longitude):
        from accounts.models import CurrentLocation, User
        CurrentLocation.objects.update_or_create(
            user=User.objects.get(id=self.driver_id),
            defaults={
                'current_latitude': latitude,
                'current_longitude': longitude,
                'timestamp': datetime.now()
            }
        )


# sandip comment part api
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



   

   
   



