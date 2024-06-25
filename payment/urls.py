from django.urls import re_path, include

from payment import views

app_name = 'trips'

urlpatterns = [
    re_path('create-order/', views.create_order),
    re_path('verify_signature/', views.verify_signature),
]