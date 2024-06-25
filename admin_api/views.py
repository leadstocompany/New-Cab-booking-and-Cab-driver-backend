from django.shortcuts import render
import pyotp
from django.conf import settings
from accounts import serializers
from rest_framework import views , permissions, status, generics
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from utility.otp import send_otp
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from admin_api.serializers import AdminLoginSerializer
from accounts.models import *
from accounts.serializers import CustomerProfileSerializer
from trips.models import Trip
from cabs.models import *
from admin_api.models import *
from admin_api.serializers import *
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from admin_api.admin_utility import  vehicle_utility, auth_utility
# Create your views here.

class AdminLoginView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AdminLoginSerializer
    def post(self, request,  *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        response=auth_utility.admin_login_view(serializer, request.data)
        return response
       
class LogoutView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the user's authentication token to log them out
        response=auth_utility.logout_view(request)
        return response
       
class AdminProfileView(views.APIView):
    serializer_class = AdminProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user
    
    
class AdminProfileUpdateView(generics.UpdateAPIView):
    parser_classes = (MultiPartParser,FormParser,JSONParser)
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user=self.request.user
        return user
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    



# Vehicle API 
class VehicleTypeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request,  *args, **kwargs):
        response =vehicle_utility.save_vehicle_type_view(request)
        return response
        
    def get(self, request):
        response=vehicle_utility.get_vehicle_type(request)
        return response

class VehicleTypeDetailsView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = CabType.objects.all()
    serializer_class = VehicleTypeSerializer


           
class VehicleClassView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        response=vehicle_utility.save_vehicle_class_view(request)
        return response
    def get(self, request, *args, **kwargs):
        model = CabClass.objects.all()
        serializer = SaveVehicleClassSerializer(model, many=True)
        response={
                'success':'true',
                'status code':status.HTTP_200_OK,
                'message':"vehilce model list.",
                'data':serializer.data,
            }
        return Response(response, status=status.HTTP_200_OK)

class VehicleClassDetailsView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = CabClass.objects.all()
    serializer_class = SaveVehicleClassSerializer

class VehicleMakerView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request,  *args, **kwargs):
        response=vehicle_utility.save_vehicle_maker_view(request)
        return response
    def get(self, request):
        response=vehicle_utility.get_vehicle_maker_view(request)
        return response

class VehicleMakerDetailsVeiw(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = VehicleMaker.objects.all()
    serializer_class = VehicleMakerSerializers      
        
class VehicleModelView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    parser_classes = (MultiPartParser,FormParser,JSONParser)
    serializer_class= SaveVehicleModelSerializer
    def post(self,request, format=None, *args, **kwargs):
        print(request.data, "request.data['model_image']")
        serializer = self.serializer_class(
            data={'model': request.data['model'], 'maker':request.data['maker'], 'model_image':request.data['model_image']},context={'request': request})
        if serializer.is_valid(raise_exception=True):
            if VehicleModel.objects.filter(model=request.data['model']).exists():
                response={
                'success':'false',
                'status code':status.HTTP_200_OK,
                'message':"vehicle model already exists."
                }
                return Response(response, status=status.HTTP_200_OK)
            serializer.save() 
            response={
                'success':'true',
                'status code':status.HTTP_201_CREATED,
                'message':"vehilce model Add Successfully.",
                'data':serializer.data,
            }
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    def get(self, request, *args, **kwargs):
        model = VehicleModel.objects.all()
        serializer = SaveVehicleModelSerializer(model, many=True)
        response={
                'success':'true',
                'status code':status.HTTP_200_OK,
                'message':"vehilce model list.",
                'data':serializer.data,
            }
        return Response(response, status=status.HTTP_200_OK)

class VehicleModelDetailsVeiw(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = VehicleModel.objects.all()
    serializer_class = SaveVehicleModelSerializer     
        


class VehicleManufacturerDetailsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    def get(self, request, *args, **kwargs):
        vehicle_type=CabType.objects.all()
        manufacturer=[]
        for cabtype in vehicle_type:
            cab_type_dict={}
            cab_type_dict['cab_type_id']=cabtype.id
            cab_type_dict['cab_type_name']=cabtype.cab_type
            cabtype_obj=CabType.objects.get(id=cabtype.id)
            vehicle_class_obj=CabClass.objects.filter(cab_type=cabtype_obj)
            vehicle_class=[]
            for cabclass in vehicle_class_obj:
                cabclass_dict={}
                cabclass_dict['cab_class_id']=cabclass.id
                cabclass_dict['cab_class_name']=cabclass.cab_class
                cabclass_dict['cab_type']=cabclass.cab_type.id
                vehicle_class.append(cabclass_dict)
            cab_type_dict['cab_class']=vehicle_class
            vehicle_maker_list=VehicleMaker.objects.filter(cab_type=cabtype_obj)
            vehicle_maker=[]
            for vehiclemaker in vehicle_maker_list:
                vehiclemaker_dict={}
                vehiclemaker_dict['maker_id']=vehiclemaker.id
                vehiclemaker_dict['maker_name']=vehiclemaker.maker
                vehiclemaker_dict['cab_type']=vehiclemaker.cab_type.id
                vehicle_maker_obj=VehicleMaker.objects.get(id=vehiclemaker.id)
                vehicle_model_list=VehicleModel.objects.filter(maker=vehicle_maker_obj)
                vehicle_model=[]
                for vehiclemodel in vehicle_model_list:
                    vehiclemodel_dict={}
                    vehiclemodel_dict['model_id']=vehiclemodel.id
                    vehiclemodel_dict['model_name']=vehiclemodel.model
                    vehiclemodel_dict['maker_id']=vehiclemodel.maker.id
                    vehicle_model.append(vehiclemodel_dict)
                vehiclemaker_dict['vehicle_model']=vehicle_model
                vehicle_maker.append(vehiclemaker_dict)
            cab_type_dict['vehicle_maker']=vehicle_maker
            manufacturer.append(cab_type_dict)
        return Response(manufacturer, status=status.HTTP_200_OK)
        







class UserDocumentFieldListCreate(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = UserDocumentField.objects.all()
    serializer_class = UserDocumentFieldSerializer

class UserDocumentFieldRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = UserDocumentField.objects.all()
    serializer_class = UserDocumentFieldSerializer


class VehicleCertificateFieldListCreate(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = VehicleCertificateField.objects.all()
    serializer_class = VehicleCertificateFieldSerializer


class VehicleCertificateFieldRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
   authentication_classes = [TokenAuthentication]
   permission_classes = [IsAuthenticated & IsAdminUser]
   queryset = VehicleCertificateField.objects.all()
   serializer_class = VehicleCertificateFieldSerializer


class FeedbackSettingListCreate(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = FeedbackSetting.objects.all()
    serializer_class =  FeedbackSettingSerializer


class FeedbackSettingRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
   authentication_classes = [TokenAuthentication]
   permission_classes = [IsAuthenticated & IsAdminUser]
   queryset = FeedbackSetting.objects.all()
   serializer_class = FeedbackSettingSerializer


