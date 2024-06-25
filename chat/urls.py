from django.urls import path
from . import views

urlpatterns = [
    path('messages/', views.MessageList.as_view()),
    path('room-name/', views.RoomNameAPIView.as_view()),
]