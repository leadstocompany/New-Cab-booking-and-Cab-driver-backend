from rest_framework import generics, status
from rest_framework.response import Response

from notifications.models import DriverNotification
from notifications.serializers import DriverNotificationSerializer
from trips.fcm_notified_task import send_fcm_notification
from utility.nearest_driver_list import get_all_available_drivers
from utility.permissions import IsAdminOrSuperuser


class DriverNotificationCreateView(generics.CreateAPIView):
    serializer_class = DriverNotificationSerializer
    permission_classes = [IsAdminOrSuperuser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()

        # Send notification to all drivers
        notification.send_notification_to_drivers()

        return Response(
            {"message": "Notification created and sent successfully"},
            status=status.HTTP_201_CREATED,
        )


class DriverNotificationListView(generics.ListAPIView):
    serializer_class = DriverNotificationSerializer
    permission_classes = [IsAdminOrSuperuser]
    queryset = DriverNotification.objects.all()


class DriverNotificationUpdateView(generics.UpdateAPIView):
    serializer_class = DriverNotificationSerializer
    permission_classes = [IsAdminOrSuperuser]
    queryset = DriverNotification.objects.all()

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
