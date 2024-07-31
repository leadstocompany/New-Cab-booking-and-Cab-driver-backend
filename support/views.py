from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DriverSupport, CustomerSupport
from .serializers import DriverSupportSerializer, CustomerSupportSerializer
from utility.permissions import IsAdminOrSuperuser
# Create your views here.



class DriverSupportCreateView(generics.CreateAPIView):
    queryset = DriverSupport.objects.all()
    serializer_class = DriverSupportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        driver = self.request.user  # assuming the user has a related driver profile
        serializer.save(driver=driver)


