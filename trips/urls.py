from django.urls import re_path, include, path

from trips import views

app_name = 'trips'

urlpatterns = [
  
    re_path(r'^trip-feedback/$', views.TripRatingAPI.as_view(),),
    re_path(r'^active-feedback-setting-list/$', views.ActiveFeedbackSettingList.as_view(),),
    re_path(r'^driver-active-feedback-page-list/$', views.DriverActiveFeedbackPageList.as_view(),),
    path('request-trip/', views.BookingRequestView.as_view(), name='request-trip'),
    path('accept-trip/', views.AcceptTripView.as_view(), name='accept-trip'),
    path('cancel-trip/', views.CancelTripView.as_view(), name='cancel_trip'),
    path('verify-otp-and-start-trip/', views.VerifyOTPAndStartTripView.as_view(), name='verify_otp_and_start_trip'),
    path('complete-trip/', views.CompleteTripView.as_view(), name='complete_trip'),
    path('arrived-at-pickup/', views.ArrivedAtPickupView.as_view(), name='arrived_at_pickup'),
    path('driver-complated-ride', views.CompletedRidesListView.as_view(), name='driver-completed-rides-list'),
    path('driver-scheduled-ride', views.ScheduledRideListView.as_view(), name='scheduled-trips-list'),
    path('driver-current-ride/', views.CurrentRidesListView.as_view(), name='current-trips-list'),
    path("passenger-ride-list/", views.PassengerTripListView.as_view(), name="passenger_ride_list")



]