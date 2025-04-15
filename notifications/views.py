from rest_framework import generics, status
from rest_framework.response import Response

from notifications.models import DriverNotification
from notifications.serializers import (
    DriverNotificationRequestSerializer,
    DriverNotificationSerializer,
)
from trips.fcm_notified_task import send_fcm_notification
from utility.nearest_driver_list import get_all_available_drivers
from utility.permissions import IsAdminOrSuperuser
from utility.pagination import CustomPagination
from rest_framework import parsers, permissions
from rest_framework.views import APIView


class DriverNotificationCreateView(generics.CreateAPIView):
    serializer_class = DriverNotificationRequestSerializer
    permission_classes = [IsAdminOrSuperuser]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if "banner" in request.FILES:
            data["banner"] = request.FILES["banner"]

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()
        notification.send_notification_to_drivers()

        return Response(
            {"message": "Notification created and sent successfully"},
            status=status.HTTP_201_CREATED,
        )


class DriverNotificationListView(generics.ListAPIView):
    serializer_class = DriverNotificationSerializer
    permission_classes = [IsAdminOrSuperuser]
    queryset = DriverNotification.objects.all()
    pagination_class = CustomPagination


class DriverNotificationDetailView(generics.RetrieveAPIView):
    serializer_class = DriverNotificationSerializer
    permission_classes = [IsAdminOrSuperuser]
    queryset = DriverNotification.objects.all()


class DriverNotificationUpdateView(generics.UpdateAPIView):
    serializer_class = DriverNotificationRequestSerializer
    permission_classes = [IsAdminOrSuperuser]
    queryset = DriverNotification.objects.all()
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()

        # Send updated notification to all drivers
        notification.send_notification_to_drivers()

        return Response({"message": "Notification updated and sent successfully"})


class DriverNotificationDeleteView(generics.DestroyAPIView):
    serializer_class = DriverNotificationSerializer
    permission_classes = [IsAdminOrSuperuser]
    queryset = DriverNotification.objects.all()
    lookup_field = "pk"


class AllDriverNotificationView(generics.ListAPIView):
    serializer_class = DriverNotificationSerializer
    parser_classes = [permissions.IsAuthenticated]
    queryset = DriverNotification.objects.all()


class NotificationMappingKeysView(APIView):
    def get(self, request, *args, **kwargs):
        mapping_keys = {
            "TripID": "Unique ID of the trip",
            "TripSource": "Source location of the trip",
            "TripDestination": "Destination location of the trip",
            "TripDistance": "Distance of the trip",
            "TripDuration": "Duration of the trip",
            "TripAmount": "Amount of the trip",
            "DriverName": "Name of the driver",
            "DriverPhone": "Phone number of the driver",
            "PassengerName": "Name of the passenger",
            "PassengerPhone": "Phone number of the passenger",
            "PaymentAmount": "Amount of the payment",
            "PaymentCurrency": "Currency of the payment",
            "PaymentStatus": "Status of the payment",
        }
        return Response(list(mapping_keys.keys()), status=200)