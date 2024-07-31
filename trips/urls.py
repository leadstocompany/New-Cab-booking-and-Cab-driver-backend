from django.urls import re_path, include, path

from trips import views

app_name = 'trips'

urlpatterns = [
    # re_path(r'^driver-trip/$', views.DriverTripAPI.as_view(),),
    re_path(r'^trip-feedback/$', views.TripRatingAPI.as_view(),),
    re_path(r'^pricing-ratio/$', views.DriverPricingRatioAPI.as_view(),),
    re_path(r'^(?P<pk>\d+)/driver-trip/$', views.DriverTripUpdateAPI.as_view(),),

    re_path(r'^active-feedback-setting-list/$', views.ActiveFeedbackSettingList.as_view(),),

    path('request-trip/', views.BookingRequestView.as_view(), name='request-trip'),
    path('accept-trip/', views.AcceptTripView.as_view(), name='accept-trip'),
   
    path('complete-trip/', views.CompleteTripView.as_view(), name='complete_trip'),
    # path('driver-payment-request/', views.PaymentRequestView.as_view(), name='driver_payment_request')
]