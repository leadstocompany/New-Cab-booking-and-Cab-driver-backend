from django.urls import path
from .views import SOSHelpRequestCreateView, SOSHelpRequestListView

urlpatterns = [
    path('sos/', SOSHelpRequestCreateView.as_view(), name='sos-request'),
    path('admin/sos-requests/', SOSHelpRequestListView.as_view(), name='sos-request-list'),
]
