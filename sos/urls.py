from django.urls import path
from .views import SOSHelpRequestCreateView, SOSHelpRequestListView, SOSHelpRequestDetailView, SOSMessageCreateView, SOSMessageListView, SOSMessageUpdateView, SOSMessageDeleteView

urlpatterns = [
    path('sos/', SOSHelpRequestCreateView.as_view(), name='sos-request'),
    path('admin/sos-requests/', SOSHelpRequestListView.as_view(), name='sos-request-list'),
    path('admin/sos-help-request/<int:pk>/', SOSHelpRequestDetailView.as_view(), name='sos-help-request-detail'),

    # sos message templates
    path('message/', SOSMessageCreateView.as_view(), name='sos-message'),
    path('message/list/', SOSMessageListView.as_view(), name='sos-message-list'),
    path('message/update/<int:pk>/', SOSMessageUpdateView.as_view(), name='sos-message-update'),
    path('message/delete/<int:pk>/', SOSMessageDeleteView.as_view(), name='sos-message-delete'),
]
