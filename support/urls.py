from django.urls import path
from support import views

urlpatterns = [
    path('driver-support/create', views.DriverSupportCreateView.as_view(), name='driver-support-create'),
    path('driver-support/', views.DriverSupportListView.as_view(), name='driver-support-list'),
    path('driver-support/<int:pk>/', views.DriverSupportDetailView.as_view(), name='driver-support-detail'),
    path('admin/driver-support/', views.AllDriverSupportListView.as_view(), name='all-driver-support-list-for-admin'),
    path('admin/driver-support/<int:pk>/', views.AdminPanelDriverSupportDetailView.as_view(), name='driver-support-detail-for-admin'),

    path('cutomer-support/create', views.CustomerSupportCreateView.as_view(), name='customer-support-create'),
    path('cutomer-support/', views.CustomerSupportListView.as_view(), name='customer-support-list'),
    path('cutomer-support/<int:pk>/', views.CustomerSupportDetailView.as_view(), name='customer-support-detail'),
    path('admin/cutomer-support/', views.AllCustomerSupportListView.as_view(), name='all-customer-support-list-for-admin'),
    path('admin/cutomer-support/<int:pk>/', views.AdminPanelCustomerSupportDetailView.as_view(), name='customer-support-detail-for-admin'),

]

