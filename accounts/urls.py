from django.urls import re_path, include, path

from accounts import views

app_name = 'accouts'

urlpatterns = [
    re_path(r'^upload/$', views.FileUploadAPI.as_view()),

    re_path(r'^driver-register/$', views.DriverRegisterAPI.as_view(),),
    re_path(r'^driver-login/$', views.DriverLoginAPI.as_view(),),
    re_path(r'^driver-otp-verify/$', views.DriverOTPVerifyLoginAPI.as_view()),
    re_path(r'^driver-profile/$', views.DriverProfileAPI.as_view()),
    re_path(r'^^(?P<pk>\d+)/get-driver-profile/$', views.GetDriverProfileAPI.as_view()),
    re_path(r'^driver-reset-password/$', views.DriverResetPasswordAPI.as_view()),

    re_path(r'^customer-register/$', views.CustomerRegisterAPI.as_view(),),
    re_path(r'^customer-otp-verify/$', views.CustomerOtpVerifyLoginAPI.as_view(),),
    re_path(r'^customer-profile/$', views.CustomerProfileAPI.as_view()),
    re_path(r'^customer-login-with-phone/$',views.LoginCustomerwithPhoneNumberApi.as_view()),
    path('active-vehiclecertificates/', views.ActiveVehicleCertificateFieldList.as_view(), name='active-vehiclecertificatefield-list'),
    path('active-userdocument/', views.ActiveUserDocumentFieldList.as_view(), name='active-userdocument-list'),
    path('active-vehicle-photo-page-data/', views.ActiveVehiclePhotoPageList.as_view(), name='active-vehicle-photo-page-list'),
  
    path('bankaccounts/create/', views.BankAccountCreateAPIView.as_view(), name='bankaccount-create'),
    path('driver/bankaccount/', views.DriverBankAccountAPIView.as_view(), name='driver-bankaccount-detail'),
    path('driver/bankaccount/update/', views.UpdateDriverBankAccountAPIView.as_view(), name='update-driver-bankaccount'),
    path('current-location/', views.CurrentLocationAPIView.as_view(), name='current-user-location'),
    # path('current-location/create/', views.CurrentLocationCreateView.as_view(), name='location-create'),
    # path('current-location/update/', views.CurrentLocationUpdateView.as_view(), name='location-update'),
    # path('current-location/', views.CurrentLocationDetailView.as_view(), name='location-detail'),
    path('active-city/', views.ActiveCityListView.as_view(), name='active-city-list'),
    path('add-fcm-token/', views.SaveFCMTokenView.as_view(), name='save-fcm-token'),
    path('driver-duty-on-off/', views.DriverDutyOnOffView.as_view(), name='drive-duaty-onoff'),
    path('driver/analytics/', views.DriverAnalyticsView.as_view(), name='driver-analytics'),
    path('driver/daily-analytics/', views.DriverDailyAnalyticsView.as_view(), name='driver-today-analytics'),
]