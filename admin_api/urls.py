from django.urls import re_path, include, path

from admin_api import views

app_name = 'admin_api'

urlpatterns = [
    path('login', views.AdminLoginView.as_view(),),
    path('logout', views.LogoutView.as_view(),),
    path('profile', views.AdminProfileView.as_view(),),
    path('profile/update',views.AdminProfileUpdateView.as_view()),
    
    # vehicle urls 
    path('vehicle-type', views.VehicleTypeListCreateView.as_view(),),
    path('vehicle-type/<int:pk>/', views.VehicleTypeDetailsView.as_view(),),
    path('vehicle-class', views.VehicleClassListCreateView.as_view(),),
    path('vehicle-class/<int:pk>/', views.VehicleClassDetailsView.as_view(),),
    path('vehicle-maker', views.VehicleMakerListCreateView.as_view(),),
    path('vehicle-maker/<int:pk>/', views.VehicleMakerDetailsVeiw.as_view(),),
    path('vehicle-model', views.VehicleModelView.as_view(),),
    path('vehicle-model/<int:pk>/', views.VehicleModelDetailsVeiw.as_view(),),
    path('vehicle-manufacturer/', views.VehicleManufacturerDetailsView.as_view(),),

    # docfield
    path('userdocumentfields/', views.UserDocumentFieldListCreate.as_view(), name='userdocumentfield-list-create'),
    path('userdocumentfields/<int:pk>/', views.UserDocumentFieldRetrieveUpdateDestroy.as_view(), name='userdocumentfield-detail'),
    path('vehiclecertificatefields/', views.VehicleCertificateFieldListCreate.as_view(), name='vehiclecertificatefield-list-create'),
    path('vehiclecertificatefields/<int:pk>/', views.VehicleCertificateFieldRetrieveUpdateDestroy.as_view(), name='vehiclecertificatefield-detail'),
    path('feedbacksetting/', views.FeedbackSettingListCreate.as_view(), name='feedbacksetting-list-create'),
    path('feedbacksetting/<int:pk>/', views.FeedbackSettingRetrieveUpdateDestroy.as_view(), name='feedbacksetting-detail'),
   
    #cabbookingPrice
    path('cabbookingprices/', views.CabBookingPriceListCreateView.as_view(), name='cabbookingprice-list-create'),
    path('cabbookingprices/<int:id>/', views.CabBookingPriceDetailView.as_view(), name='cabbookingprice-detail'),

    # Driver api  
    path('driver/', views.DriverListCreateView.as_view(), name='driver-list-create'),
    path('driver/<int:id>/', views.DriverDetailView.as_view(), name='drivers-detail'),


    # Passengers api  
    path('passengers/', views.PassengersListCreateView.as_view(), name='passengers-list-create'),
    path('passenger/<int:id>/', views.PassengersDetailView.as_view(), name='passenger-detail'),


     # Passengers api  
    path('vehicles/', views.VehicleListCreateView.as_view(), name='vehicle-list-create'),
    path('vehicle/<int:id>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
]
