from django.urls import path
from .views import SOSHelpRequestCreateView, SOSHelpRequestListView, SOSHelpRequestDetailView

urlpatterns = [
    path('sos/', SOSHelpRequestCreateView.as_view(), name='sos-request'),
    path('admin/sos-requests/', SOSHelpRequestListView.as_view(), name='sos-request-list'),
    path('admin/sos-help-request/<int:pk>/', SOSHelpRequestDetailView.as_view(), name='sos-help-request-detail'),
]
