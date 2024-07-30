from django.shortcuts import render
from rest_framework import generics, permissions
from .models import SOSHelpRequest
from .serializers import *
from rest_framework import generics
from .tasks import send_sos_notification
from utility.permissions import IsAdminOrSuperuser
# Create your views here.

class SOSHelpRequestCreateView(generics.CreateAPIView):
    serializer_class = SOSHelpRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        sos_request = serializer.save(user=self.request.user)
        send_sos_notification(sos_request.id)


class SOSHelpRequestListView(generics.ListAPIView):
    queryset = SOSHelpRequest.objects.all()
    serializer_class = SOSHelpRequstSerializer
    permission_classes = [IsAdminOrSuperuser]