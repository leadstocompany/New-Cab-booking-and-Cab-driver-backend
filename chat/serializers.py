from rest_framework import serializers
from .models import Message, O2ORoom

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ('id', 'timestamp')

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = O2ORoom
        exclude = ('updated_at',)