from django.urls import include, re_path

from cabs import views

app_name = 'cabs'

urlpatterns = [
    re_path(r'^details/$', views.VehicaleDetailsAPI.as_view(),),
    re_path(r'^(?P<pk>\d+)/get-vehicle/$', views.GetVehicaleDetailsAPI.as_view(),),
    re_path(r'^(?P<pk>\d+)/vehicle-maker/$', views.VehicleMakerAPI.as_view(),),
    re_path(r'^(?P<pk>\d+)/vehicle-model/$', views.VehicleModelAPI.as_view(),),
    re_path(r'^cab-type/$', views.CabTypeAPI.as_view(),),
    re_path(r'^(?P<pk>\d+)/cab-class/$', views.CabClassAPI.as_view(),),
    re_path(r'^(?P<pk>\d+)/update-location/$', views.VehicleLocationUpdateAPI.as_view(),), 
]