from django.urls import path
from .views import ActiveSOSRequestCountView, SOSHelpRequestCreateView, SOSHelpRequestListView, SOSHelpRequestDetailView, SOSMessageCreateView, SOSMessageListView, SOSMessageUpdateView, SOSMessageDeleteView, ActivateSOSHelpRequestList, CompletedSOSHelpRequestList, SOSHelpRequestDetail, ResolveSOSRequestView

urlpatterns = [
    path('sos/', SOSHelpRequestCreateView.as_view(), name='sos-request'),
    path('admin/sos-requests/', SOSHelpRequestListView.as_view(), name='sos-request-list'),
    path('admin/sos-help-request/<int:pk>/', SOSHelpRequestDetailView.as_view(), name='sos-help-request-detail'),

    # sos message templates
    path('message/', SOSMessageCreateView.as_view(), name='sos-message'),
    path('message/list/', SOSMessageListView.as_view(), name='sos-message-list'),
    path('message/update/<int:pk>/', SOSMessageUpdateView.as_view(), name='sos-message-update'),
    path('message/delete/<int:pk>/', SOSMessageDeleteView.as_view(), name='sos-message-delete'),

    # sos admin
    path('admin/active/', ActivateSOSHelpRequestList.as_view(), name='sos-help-request-list'),
    path('admin/completed/', CompletedSOSHelpRequestList.as_view(), name='completed-sos-help-request-list'),
    path('admin/sos-requests/<int:pk>/details/', SOSHelpRequestDetail.as_view(), name='sos-help-request-detail'),
    path('admin/sos-requests/<int:pk>/update/', ResolveSOSRequestView.as_view(), name='sos-help-request-update'),
    path('admin/active/count/', ActiveSOSRequestCountView.as_view(), name='active-sos-count'),

]
