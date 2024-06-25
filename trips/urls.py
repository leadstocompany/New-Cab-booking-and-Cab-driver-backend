from django.urls import re_path, include

from trips import views

app_name = 'trips'

urlpatterns = [
    re_path(r'^driver-trip/$', views.DriverTripAPI.as_view(),),
    re_path(r'^trip-feedback/$', views.DriverPricingRatioAPI.as_view(),),
    re_path(r'^pricing-ratio/$', views.DriverPricingRatioAPI.as_view(),),
    re_path(r'^(?P<pk>\d+)/driver-trip/$', views.DriverTripUpdateAPI.as_view(),),

    re_path(r'^active-feedback-setting-list/$', views.ActiveFeedbackSettingList.as_view(),),
]