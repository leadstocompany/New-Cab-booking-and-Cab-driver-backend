from django.urls import include, re_path, path

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
    path('cabclasswithprices/', views.CabClassWithPriceList.as_view(), name='cabclassprice-list'),
    # path('nearby-vehicles/', views.NearbyVehiclesAPIView.as_view(), name='nearby-vehicles'),
    # # http://127.0.0.1:8000/nearby-vehicles/?latitude=12.9715987&longitude=77.594566&cab_class=1
    path('nearest-drivers/<int:cab_class_id>/<str:latitude>/<str:longitude>/', views.NearestDriversView.as_view(), name='nearest-drivers'),

]