from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from utility.pagination import CustomPagination
from .models import SOSHelpRequest, SOSMessage
from .serializers import (
    AllSOSMessageSerializer,
    SOSHelpRequestDetailSerializer,
    SOSHelpRequestSerializer,
    SOSMessageSerializer,
    SOSHelpRequestListSerializer,
)
from rest_framework import generics
from .tasks import send_sos_notification
from utility.permissions import IsAdminOrSuperuser
import logging
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView


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
    lookup_field = "pk"

    def get(self, request, *args, **kwargs):
        try:
            sos_help_request = SOSHelpRequest.objects.get(pk=kwargs["pk"])
            serializer = self.get_serializer(sos_help_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SOSHelpRequest.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response(
                {"error": "SOSHelpRequest entry not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class SOSMessageCreateView(generics.CreateAPIView):
    queryset = SOSMessage.objects.all()
    serializer_class = SOSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]


class SOSMessageListView(generics.ListAPIView):
    queryset = SOSMessage.objects.all()
    serializer_class = SOSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

class AllSOSMessageList(generics.ListAPIView):
    queryset = SOSMessage.objects.all()
    serializer_class = SOSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

class SOSMessageUpdateView(generics.UpdateAPIView):
    queryset = SOSMessage.objects.all()
    serializer_class = SOSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

class SOSMessageDetailView(generics.RetrieveAPIView):
    queryset = SOSMessage.objects.all()
    serializer_class = SOSMessageSerializer
    permission_classes = [IsAdminOrSuperuser]
    lookup_field = "pk"

    def get(self, request, *args, **kwargs):
        try:
            sos_help_request = SOSMessage.objects.get(pk=kwargs["pk"])
            serializer = self.get_serializer(sos_help_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SOSMessage.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response(
                {"error": "SOSMessage entry not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class SOSMessageDeleteView(generics.DestroyAPIView):
    queryset = SOSMessage.objects.all()
    serializer_class = SOSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"


class ActivateSOSHelpRequestList(generics.ListAPIView):
    queryset = SOSHelpRequest.objects.filter(resolved=False).order_by("-created_at")
    serializer_class = SOSHelpRequestListSerializer
    permission_classes = [IsAdminOrSuperuser]
    pagination_class = CustomPagination


class CompletedSOSHelpRequestList(generics.ListAPIView):
    queryset = SOSHelpRequest.objects.filter(resolved=True)
    serializer_class = SOSHelpRequestListSerializer
    permission_classes = [IsAuthenticated]  # Allow authenticated users
    pagination_class = CustomPagination

    def get_queryset(self):
        return SOSHelpRequest.objects.filter(resolved=True).order_by("-created_at")


class SOSHelpRequestDetail(generics.RetrieveAPIView):
    queryset = SOSHelpRequest.objects.all()
    serializer_class = SOSHelpRequestDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get(self, request, *args, **kwargs):
        try:
            sos_help_request = SOSHelpRequest.objects.get(pk=kwargs["pk"])
            serializer = self.get_serializer(sos_help_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SOSHelpRequest.DoesNotExist:
            logger.error(f"SOSHelpRequest with id {kwargs['pk']} not found")
            return Response(
                {"error": "SOSHelpRequest entry not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ResolveSOSRequestView(generics.UpdateAPIView):
    queryset = SOSHelpRequest.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        try:
            sos_request = self.get_object()
            sos_request.resolved = True
            sos_request.save()
            return Response(
                {"message": "SOS request marked as resolved"}, status=status.HTTP_200_OK
            )
        except SOSHelpRequest.DoesNotExist:
            return Response(
                {"error": "SOS request not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ActiveSOSRequestCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        active_count = SOSHelpRequest.objects.filter(resolved=False).count()
        return Response({"active_sos_count": active_count}, status=status.HTTP_200_OK)
