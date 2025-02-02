from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import SOSHelpRequest, SOSMessage
from .serializers import SOSHelpRequestSerializer, SOSMessageSerializer
from rest_framework import generics
from .tasks import send_sos_notification
from utility.permissions import IsAdminOrSuperuser
import logging
logger = logging.getLogger(__name__)
# Create your views here.

class SOSHelpRequestCreateView(generics.CreateAPIView):
    serializer_class = SOSHelpRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        sos_request = serializer.save(user=self.request.user)
        send_sos_notification.delay(sos_request.id)


class SOSHelpRequestListView(generics.ListAPIView):
    queryset = SOSHelpRequest.objects.all()
    serializer_class = SOSHelpRequestSerializer
    permission_classes = [IsAdminOrSuperuser]



class SOSHelpRequestDetailView(generics.RetrieveAPIView):
    queryset = SOSHelpRequest.objects.all()
    serializer_class = SOSHelpRequestSerializer
    permission_classes = [IsAdminOrSuperuser]
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        try:
            sos_help_request = SOSHelpRequest.objects.get(pk=kwargs['pk'])
            serializer = self.get_serializer(sos_help_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SOSHelpRequest.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "SOSHelpRequest entry not found."}, status=status.HTTP_404_NOT_FOUND)
        
class SOSMessageCreateView(generics.CreateAPIView):
    queryset = SOSMessage.objects.all()
    serializer_class = SOSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

class SOSMessageListView(generics.ListAPIView):
    queryset = SOSMessage.objects.all()
    serializer_class = SOSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

class SOSMessageUpdateView(generics.UpdateAPIView):
    queryset = SOSMessage.objects.all()
    serializer_class = SOSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

class SOSMessageDeleteView(generics.DestroyAPIView):
    queryset = SOSMessage.objects.all()
    serializer_class = SOSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'