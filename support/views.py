from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DriverSupport, CustomerSupport
from .serializers import DriverSupportSerializer, CustomerSupportSerializer
from utility.permissions import IsAdminOrSuperuser
import logging
logger = logging.getLogger(__name__)
# Create your views here.



class DriverSupportCreateView(generics.CreateAPIView):
    queryset = DriverSupport.objects.all()
    serializer_class = DriverSupportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        driver = self.request.user  # assuming the user has a related driver profile
        serializer.save(driver=driver)


class DriverSupportListView(generics.ListAPIView):
    queryset = DriverSupport.objects.all().order_by('-created_at')
    serializer_class = DriverSupportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Optionally, you can filter the queryset by the authenticated driver
        driver = self.request.user  # assuming the user has a related driver profile
        return DriverSupport.objects.filter(driver=driver)


class DriverSupportDetailView(generics.RetrieveAPIView):
    queryset = DriverSupport.objects.all()
    serializer_class = DriverSupportSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        driver = self.request.user  # Assuming the user has a related driver profile
        try:
            driver_support = DriverSupport.objects.get(pk=kwargs['pk'], driver=driver)
            serializer = self.get_serializer(driver_support)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DriverSupport.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "DriverSupport entry not found or does not belong to the authenticated driver."}, status=status.HTTP_404_NOT_FOUND)



class AllDriverSupportListView(generics.ListAPIView):
    queryset = DriverSupport.objects.all().order_by('-created_at')
    serializer_class = DriverSupportSerializer
    permission_classes = [IsAdminOrSuperuser]



class AdminPanelDriverSupportDetailView(generics.RetrieveAPIView):
    queryset = DriverSupport.objects.all()
    serializer_class = DriverSupportSerializer
    permission_classes = [IsAdminOrSuperuser]
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        try:
            driver_support = DriverSupport.objects.get(pk=kwargs['pk'])
            serializer = self.get_serializer(driver_support)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DriverSupport.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "DriverSupport entry not found."}, status=status.HTTP_404_NOT_FOUND)
        




# customer support 
class CustomerSupportCreateView(generics.CreateAPIView):
    queryset = CustomerSupport.objects.all()
    serializer_class = CustomerSupportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        customer = self.request.user  # assuming the user has a related driver profile
        serializer.save(customer=customer)


class CustomerSupportListView(generics.ListAPIView):
    queryset = CustomerSupport.objects.all().order_by('-created_at')
    serializer_class = CustomerSupportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Optionally, you can filter the queryset by the authenticated driver
        customer = self.request.user  # assuming the user has a related driver profile
        return CustomerSupport.objects.filter(customer=customer)


class CustomerSupportDetailView(generics.RetrieveAPIView):
    queryset = CustomerSupport.objects.all()
    serializer_class = CustomerSupportSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        customer = self.request.user  # Assuming the user has a related driver profile
        try:
            customer_support = CustomerSupport.objects.get(pk=kwargs['pk'], customer=customer)
            serializer = self.get_serializer(customer_support)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomerSupport.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "CustomerSupport entry not found or does not belong to the authenticated driver."}, status=status.HTTP_404_NOT_FOUND)



class AllCustomerSupportListView(generics.ListAPIView):
    queryset = CustomerSupport.objects.all().order_by('-created_at')
    serializer_class = CustomerSupportSerializer
    permission_classes = [IsAdminOrSuperuser]



class AdminPanelCustomerSupportDetailView(generics.RetrieveAPIView):
    queryset = CustomerSupport.objects.all()
    serializer_class = CustomerSupportSerializer
    permission_classes = [IsAdminOrSuperuser]
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        try:
            customer_support = CustomerSupport.objects.get(pk=kwargs['pk'])
            serializer = self.get_serializer(customer_support)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomerSupport.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "CustomerSupport entry not found."}, status=status.HTTP_404_NOT_FOUND)