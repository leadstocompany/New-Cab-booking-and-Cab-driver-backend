from django.urls import path

from . import views

urlpatterns = [
    path(
        "admin/list/",
        views.DriverNotificationListView.as_view(),
        name="list_notifications",
    ),
    path(
        "admin/create/",
        views.DriverNotificationCreateView.as_view(),
        name="create_notifications",
    ),
    path(
        "admin/<int:pk>/",
        views.DriverNotificationUpdateView.as_view(),
        name="update_notifications",
    ),
    path(
        "admin/<int:pk>/",
        views.DriverNotificationDeleteView.as_view(),
        name="delete_notifications",
    ),
]
