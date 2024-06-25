from rest_framework import generics
from rest_framework.views import APIView
from .models import Message, O2ORoom
from .serializers import MessageSerializer, RoomSerializer
from rest_framework import status
from rest_framework.response import Response

class MessageList(generics.ListAPIView):
    serializer_class = MessageSerializer
    ordering = ('-timestamp',)
    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)
    


class RoomNameAPIView(APIView):
    def post(self, request, *args, **kwargs):
        sender_receiver = request.data.get('sender_receiver')
        print(type(sender_receiver))
        if type(sender_receiver) == list:
            room_obj, _ = O2ORoom.objects.get_or_create(sender_receiver=sorted(sender_receiver))
            room_data = RoomSerializer(room_obj).data
            return Response(data={"room": room_data}, status=status.HTTP_200_OK)
        else:
            return Response(data={"error": "sender_receiver must be in list."}, status=status.HTTP_400_BAD_REQUEST)