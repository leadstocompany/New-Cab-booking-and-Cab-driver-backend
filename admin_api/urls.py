from django.urls import re_path, include, path
from rest_framework.routers import DefaultRouter


from admin_api import views
from admin_api.views import NotificationTypeChoicesView

app_name = 'admin_api'



urlpatterns = [
    path('login', views.AdminLoginView.as_view(),),
    path('logout', views.LogoutView.as_view(),),
    path('profile', views.AdminProfileView.as_view(),),
    path('profile/update',views.AdminProfileUpdateView.as_view()),

    # dashboard urls
    path('dashboard', views.DashboardAPI.as_view(),),
    
    # vehicle urls 
    path('vehicle-type', views.VehicleTypeListCreateView.as_view(),),
    path('vehicle-type/<int:pk>/', views.VehicleTypeDetailsView.as_view(),),
    path('cabtypes/delete/<int:pk>/', views.CabTypeDeleteView.as_view(), name='cabtype-delete'),
    path('vehicle-class', views.VehicleClassListCreateView.as_view(),),
    path('vehicle-class/<int:pk>/', views.VehicleClassDetailsView.as_view(),),
    path('cabclasses/delete/<int:pk>/', views.CabClassDeleteView.as_view(), name='cabclass-delete'),
    path('vehicle-maker', views.VehicleMakerListCreateView.as_view(),),
    path('vehicle-maker/<int:pk>/', views.VehicleMakerDetailsVeiw.as_view(),),
    path('vehiclemaker/delete/<int:pk>/', views.VehicleMakerDeleteView.as_view(), name='vehiclemaker-delete'),
    path('vehicle-model', views.VehicleModelView.as_view(),),
    path('vehicle-model/<int:pk>/', views.VehicleModelDetailsVeiw.as_view(),),
    path('vehiclemodel/delete/<int:pk>/', views.VehicleModelDeleteView.as_view(), name='vehiclemodel-delete'),
    # path('vehicle-manufacturer/', views.VehicleManufacturerDetailsView.as_view(),),

    # docfield
    path('userdocumentfields/', views.UserDocumentFieldListCreate.as_view(), name='userdocumentfield-list-create'),
    path('userdocumentfields/<int:pk>/', views.UserDocumentFieldRetrieveUpdateDestroy.as_view(), name='userdocumentfield-detail'),
    path('vehiclecertificatefields/', views.VehicleCertificateFieldListCreate.as_view(), name='vehiclecertificatefield-list-create'),
    path('vehiclecertificatefields/<int:pk>/', views.VehicleCertificateFieldRetrieveUpdateDestroy.as_view(), name='vehiclecertificatefield-detail'),
   
    path('feedbacksetting/', views.FeedbackSettingListCreate.as_view(), name='feedbacksetting-list-create'),
    path('feedbacksetting/<int:pk>/', views.FeedbackSettingRetrieveUpdateDestroy.as_view(), name='feedbacksetting-detail'),
    path('driver-feedback-page/', views.DriverFeedbackPageListCreate.as_view(), name='driverfeedbackpage-list-create'),
    path('driver-feedback-page/<int:pk>/', views.DriverFeedbackPageRetrieveUpdateDestroy.as_view(), name='driverfeedbackpage-detail'),
   
    #cabbookingPrice
    path('cabbookingprices/', views.CabBookingPriceListCreateView.as_view(), name='cabbookingprice-list-create'),
    path('cabbookingprices/<int:id>/', views.CabBookingPriceDetailView.as_view(), name='cabbookingprice-detail'),

    # Driver api  
    path('driver/', views.DriverCreateView.as_view(), name='driver-create'),
    path('drivers/', views.DriverListView.as_view(), name='driver-list'),
    path('new-drivers/', views.PendingDriverListAPIView.as_view(), name='pending-driver-list'),
    path('rejected-drivers/', views.RejectedDriverListAPIView.as_view(), name='rejected-driver-list'),
    path('suspended-drivers/', views.SuspendedDriverListAPIView.as_view(), name='rejected-driver-list'),
    path('driver/<int:id>/update/', views.DriverUpdateView.as_view(), name='drivers-update'),
    path('driver/<int:id>/delete/', views.DriverDeleteView.as_view(), name='driver-delete'),
    path('driver/<int:id>/details/', views.DriverDetailView.as_view(), name='drivers-detail'),
    


    # Passengers api  
    path('passengers/', views.PassengersListCreateView.as_view(), name='passengers-list-create'),
    path('passenger/<int:id>/', views.PassengersDetailView.as_view(), name='passenger-detail'),


     # Passengers api  
    path('vehicles/', views.VehicleListCreateView.as_view(), name='vehicle-list-create'),
    path('vehicle/<int:id>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('vehicle/delete/<int:pk>/', views.VehicleDeleteView.as_view(), name='vehicle-delete'),

    # trip api 
    path('active-trips/', views.ActiveTripList.as_view(), name='active-trip-list'),
    path('completed-trips/', views.CompletedTripList.as_view(), name='completed-trip-list'),
    path('booked-trips/', views.BookedTripList.as_view(), name='booked-trip-list'),
    path('scheduled-trips/', views.ScheduledTripList.as_view(), name='schedule-trip-list'),
    path('trip/<int:trip_id>/', views.TripDetailView.as_view(), name='admin-trip-detail'),


    path('trip-rating-feedback-list/', views.TripRatingFeedbackList.as_view(), name='trip-rating-feedback-list'),

    path('vehicle-photo-page/', views.VehiclePhotoPageListCreate.as_view(), name='vehicle-photo-page-list-create'),
    path('vehicle-photo-page/<int:pk>/', views.VehiclePhotoPageRetrieveUpdateDestroy.as_view(), name='vehicle-photo-page-detail'),


    # city api 
    path('city/', views.CityListCreate.as_view(), name='city-list-create'),
    path('city/<int:pk>/', views.CityRetrieveUpdateDestroy.as_view(), name='city-detail'),

    # driver vehicle block and unblock api 
    path('driver/block/', views.BlockDriverProfileAPIView.as_view(), name='block-driver'),
    path('driver/unblock/', views.UnBlockDriverProfileAPIView.as_view(), name='unblock-driver'),
    path('driver/approve/', views.ApproveDriverProfileAPIView.as_view(), name='approve-driver'),
    path('driver/reject/', views.RejectDriverProfileAPIView.as_view(), name='reject-driver'),

    # email template
    path('email-templates/', views.EmailTemplateListCreateView.as_view(), name='email-template-list-create'),
    path('email-templates/<int:pk>/', views.EmailTemplateRetrieveUpdateDestroyView.as_view(), name='email-template-detail'),

    path('notification-templates/', views.NotificationTemplateListCreateView.as_view(), name='notification-template-list-create'),
    path('notification-templates/<int:pk>/', views.NotificationTemplateRetrieveUpdateDestroyView.as_view(), name='notification-template-detail'),

    path('notification-types/', NotificationTypeChoicesView.as_view(), name='notification-type-choices'),
]
