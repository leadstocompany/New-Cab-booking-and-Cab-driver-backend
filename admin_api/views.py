from django.shortcuts import render
import pyotp
from django.conf import settings
from accounts import serializers
from rest_framework import views , permissions, status, generics, mixins
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
from cabs.serializers import CabBookingPriceSerializer
from utility.permissions import IsAdminOrSuperuser
import json
from admin_api.serializers import  CitySerializer, VehicleTypeSerializer, SaveVehicleClassSerializer, VehicleMakerSerializers, SaveVehicleModelSerializer, VehicleSerializer, DriverListSerializer, DriverDetailsSerializer
from admin_api.admin_utility import auth_utility
from utility.pagination import CustomPagination
from accounts.models import Driver, Customer
from accounts.serializers import DriverProfileSerializer, CustomerProfileSerializer
from trips.serializers import TripSerializer, TripRatingSerializer
from trips.models import TripRating
from payment.models import Bill_Payment
from wallets.models import *
from rest_framework.exceptions import NotFound
from django.db.models import ProtectedError
from rest_framework.exceptions import APIException

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


class  VehicleTypeListCreateView(generics.ListCreateAPIView):
    # parser_classes = (MultiPartParser,FormParser,JSONParser)
    queryset = CabType.objects.all().order_by("-created_at")
    serializer_class =  VehicleTypeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrSuperuser]

class VehicleTypeDetailsView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    # parser_classes = (MultiPartParser,FormParser,JSONParser)
    queryset = CabType.objects.all()
    serializer_class = VehicleTypeSerializer

class CabTypeDeleteView(generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = CabType.objects.all()
    serializer_class = CabTypeSerializer
    lookup_field = 'pk'
    
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
              # Custom error message formatting
            related_objects = e.protected_objects  # Get the related objects causing the error
            model_names = {obj._meta.verbose_name for obj in related_objects}  # Collect model names causing the error
            model_list = ', '.join(model_names)  # Create a comma-separated list of model names
            raise APIException(f"Cannot delete this CabType because it is referenced by the following models: {model_list}.")
        except Exception as e:
            raise APIException(f"Error deleting CabType: {str(e)}")
           

class VehicleClassListCreateView(generics.ListCreateAPIView):
    # parser_classes = (MultiPartParser,FormParser,JSONParser)
    queryset = CabClass.objects.all().order_by("-created_at")
    serializer_class = SaveVehicleClassSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrSuperuser]
class VehicleClassDetailsView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    # parser_classes = (MultiPartParser,FormParser,JSONParser)
    queryset = CabClass.objects.all()
    serializer_class = SaveVehicleClassSerializer

class CabClassDeleteView(generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = CabClass.objects.all()
    serializer_class = CabClassSerializer
    lookup_field = 'pk'
    
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
             # Custom error message formatting
            related_objects = e.protected_objects  # Get the related objects causing the error
            model_names = {obj._meta.verbose_name for obj in related_objects}  # Collect model names causing the error
            model_list = ', '.join(model_names)  # Create a comma-separated list of model names
            raise APIException(f"Cannot delete CabClass as it is referenced by the following models: {model_list}.")
            # raise APIException(f"Error deleting CabClass: {str(e)}")
        except Exception as e:
            raise APIException(f"Error deleting CabClass: {str(e)}")
           

class VehicleMakerListCreateView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrSuperuser]
    # parser_classes = (MultiPartParser,FormParser,JSONParser)
    queryset = VehicleMaker.objects.all().order_by("-created_at")
    serializer_class =  VehicleMakerSerializers
   


class VehicleMakerDetailsVeiw(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    # parser_classes = (MultiPartParser,FormParser,JSONParser)
    queryset = VehicleMaker.objects.all()
    serializer_class = VehicleMakerSerializers  


class VehicleMakerDeleteView(generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = VehicleMaker.objects.all()
    serializer_class = VehicleMakerSerializer
    lookup_field = 'pk'
    
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Custom error message formatting
            related_objects = e.protected_objects  # Get the related objects causing the error
            model_names = {obj._meta.verbose_name for obj in related_objects}  # Collect model names causing the error
            model_list = ', '.join(model_names)  # Create a comma-separated list of model names
            raise APIException(f"Cannot delete this VehicleMaker because it is referenced by the following models: {model_list}.")
        except Exception as e:
            raise APIException(f"Error deleting VehicleMaker: {str(e)}")

        
class VehicleModelView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    # parser_classes = (MultiPartParser,FormParser,JSONParser)
    serializer_class= SaveVehicleModelSerializer
    def post(self,request, format=None, *args, **kwargs):
        serializer = self.serializer_class(
            data={'model': request.data['model'],'cabtype':request.data['cabtype'],'cabclass':request.data['cabclass'], 'maker':request.data['maker'], 'model_image':request.data['model_image']},context={'request': request})
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
        model = VehicleModel.objects.all().order_by("-created_at")
        serializer = SaveVehicleModelSerializer(model, many=True)
        response={
                'success':'true',
                'status code':status.HTTP_200_OK,
                'message':"vehilce model list.",
                'data':serializer.data,
            }
        return Response(response, status=status.HTTP_200_OK)

# class VehicleModelListCreateView(generics.ListCreateAPIView):
#     queryset = VehicleModel.objects.all()
#     serializer_class =  SaveVehicleModelSerializer
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAdminOrSuperuser]

class VehicleModelDetailsVeiw(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    # parser_classes = (MultiPartParser,FormParser,JSONParser)
    queryset = VehicleModel.objects.all()
    serializer_class = SaveVehicleModelSerializer   


class VehicleModelDeleteView(generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = VehicleModel.objects.all()
    serializer_class = VehicleModelSerializer
    lookup_field = 'pk'
    
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Custom error message formatting
            related_objects = e.protected_objects
            model_names = {obj._meta.verbose_name for obj in related_objects}
            model_list = ', '.join(model_names)
            raise APIException(f"Cannot delete this VehicleModel because it is referenced by the following models: {model_list}.")
        except Exception as e:
            raise APIException(f"Error deleting VehicleModel: {str(e)}")
        








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


class CabBookingPriceListCreateView(generics.ListCreateAPIView):
    queryset = CabBookingPrice.objects.all()
    serializer_class = CabBookingPriceSerializer
    permission_classes = [IsAdminOrSuperuser]

class CabBookingPriceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CabBookingPrice.objects.all()
    serializer_class = CabBookingPriceSerializer
    permission_classes = [IsAdminOrSuperuser]
    lookup_field = 'id'




class DriverCreateView(generics.CreateAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverProfileCreateSerializer
    permission_classes = [IsAdminOrSuperuser]
   

class DriverListView(generics.ListAPIView):
    # queryset = Driver.objects.all().order_by("-date_joined")
    queryset=User.objects.filter(type=User.Types.DRIVER, profile_status__in=['Pending','Approve']).order_by("-date_joined")
    serializer_class = DriverListSerializer
    permission_classes = [IsAdminOrSuperuser]
    pagination_class = CustomPagination  

class PendingDriverListAPIView(generics.ListAPIView):
    serializer_class = DriverListSerializer
    permission_classes = [IsAdminOrSuperuser]
    pagination_class = CustomPagination
    def get_queryset(self):
        return User.objects.filter(type=User.Types.DRIVER, profile_status='Pending').order_by("-date_joined")
    
class RejectedDriverListAPIView(generics.ListAPIView):
    serializer_class = DriverListSerializer
    permission_classes = [IsAdminOrSuperuser]
    pagination_class = CustomPagination
    def get_queryset(self):
        return User.objects.filter(type=User.Types.DRIVER, profile_status='Rejected').order_by("-date_joined")

    
class SuspendedDriverListAPIView(generics.ListAPIView):
    serializer_class = DriverListSerializer
    permission_classes = [IsAdminOrSuperuser]
    pagination_class = CustomPagination
    def get_queryset(self):
        return User.objects.filter(type=User.Types.DRIVER, profile_status='Block').order_by("-date_joined")


class DriverUpdateView(mixins.UpdateModelMixin,
                       generics.GenericAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverProfileSerializer
    permission_classes = [IsAdminOrSuperuser]  
    lookup_field = 'id'
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

   
class DriverDeleteView(generics.DestroyAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverProfileSerializer
    permission_classes = [IsAdminUser]  # Only admins can delete drivers
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        driver = self.get_object()

        # Manually delete or disassociate related vehicles before deleting the driver
        try:
            # Option 1: Delete the related vehicles
            Vehicle.objects.filter(driver=driver).delete()
         
            BankAccount.objects.filter(driver=driver).delete()
            Wallet.objects.filter(user=driver).delete()
            CurrentLocation.objects.filter(user=driver).delete()
            # Option 2: Disassociate (set driver to None) if the foreign key allows it
            # Vehicle.objects.filter(driver=driver).update(driver=None)

            # Now delete the driver
            return self.destroy(request, *args, **kwargs)
        except ProtectedError as e:
            driver.profile_status="Block"
            driver.driver_duty=False
            driver.save()
            return Response(
                {"message":"Cannot delete the 'Driver'details,  because they are referenced of driver trip, subcription data, So that way we update the driver data and Block the driver"},
                # {"error": str(e)},
                status=status.HTTP_200_OK
            )

class DriverDetailView(generics.RetrieveAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverDetailsSerializer
    permission_classes = [IsAdminOrSuperuser]  
    lookup_field = 'id'


class PassengersListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all().order_by("-date_joined")
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAdminOrSuperuser]
    pagination_class = CustomPagination  



class PassengersDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAdminOrSuperuser]  
    lookup_field = 'id'




class VehicleListCreateView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all().order_by("-created_at")
    serializer_class = VehicleSerializer
    permission_classes = [IsAdminOrSuperuser]
    pagination_class = CustomPagination  



class VehicleDetailView(generics.RetrieveUpdateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAdminOrSuperuser]  
    lookup_field = 'id'


class VehicleDeleteView(generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    lookup_field = 'pk'
    
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError as e:
            # Custom error message formatting
            related_objects = e.protected_objects
            model_names = {obj._meta.verbose_name for obj in related_objects}
            model_list = ', '.join(model_names)
            raise APIException(f"Cannot delete this Vehicle because it is referenced by the following models: {model_list}.")
        except Exception as e:
            raise APIException(f"Error deleting Vehicle: {str(e)}")



class DriverFeedbackPageListCreate(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & IsAdminUser]
    queryset = DriverFeedbackPage.objects.all()
    serializer_class =  DriverFeedbackPageSerializer


class DriverFeedbackPageRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
   authentication_classes = [TokenAuthentication]
   permission_classes = [IsAuthenticated & IsAdminUser]
   queryset = DriverFeedbackPage.objects.all()
   serializer_class = DriverFeedbackPageSerializer



class ActiveTripList(generics.ListAPIView):
    permission_classes = [IsAdminOrSuperuser]  
    serializer_class = TripSerializer
    pagination_class = CustomPagination 
    def get_queryset(self):
        return Trip.objects.filter(status="ON_TRIP").order_by("-created_at")



class CompletedTripList(generics.ListAPIView):
    permission_classes = [IsAdminOrSuperuser]  
    serializer_class = TripSerializer
    pagination_class = CustomPagination 
    def get_queryset(self):
        return Trip.objects.filter(status="COMPLETED").order_by("-created_at")
    
class BookedTripList(generics.ListAPIView):
    permission_classes = [IsAdminOrSuperuser]  
    serializer_class = TripSerializer
    pagination_class = CustomPagination 
    def get_queryset(self):
        return Trip.objects.filter(status="BOOKED").order_by("-created_at")
class ScheduledTripList(generics.ListAPIView):
    permission_classes = [IsAdminOrSuperuser]  
    serializer_class = TripSerializer
    pagination_class = CustomPagination 
    def get_queryset(self):
        return Trip.objects.filter(status="BOOKED", scheduled_datetime__isnull=False).order_by("-created_at")

class TripDetailView(generics.RetrieveAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    lookup_field = 'trip_id'

    def get(self, request, *args, **kwargs):
        try:
            trip = self.get_object()
            serializer = TripSerializer(trip)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Trip.DoesNotExist:
            return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)
        
class TripRatingFeedbackList(generics.ListAPIView):
    permission_classes = [IsAdminOrSuperuser]  
    serializer_class = TripRatingSerializer
    pagination_class = CustomPagination 
    def get_queryset(self):
        return TripRating.objects.all().order_by("-created_at")


class VehiclePhotoPageListCreate(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes =[IsAdminOrSuperuser] 
    queryset = VehiclePhotoPage.objects.all()
    serializer_class = VehiclePhotoPageSerializer


class VehiclePhotoPageRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
   authentication_classes = [TokenAuthentication]
   permission_classes = [IsAdminOrSuperuser] 
   queryset = VehiclePhotoPage.objects.all()
   serializer_class = VehiclePhotoPageSerializer
   


class CityListCreate(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes =[IsAdminOrSuperuser] 
    queryset = City.objects.all().order_by("-created_at")
    serializer_class = CitySerializer


class CityRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
   authentication_classes = [TokenAuthentication]
   permission_classes = [IsAdminOrSuperuser] 
   queryset = City.objects.all()
   serializer_class = CitySerializer



class BlockDriverProfileAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrSuperuser] 

    def post(self, request, *args, **kwargs):
        # Getting data from the request
        # driver_id = kwargs.get('driver_id')
        driver_id = request.data.get("driver_id")
        # Fetch the driver and vehicle instances
        try:
            driver = User.objects.get(id=driver_id, type=User.Types.DRIVER)
        except User.DoesNotExist:
            raise NotFound(detail="Driver not found.")

         # Block the driver profile
        driver.profile_status = 'Block'
        driver.save()
        if Vehicle.objects.filter(driver=driver).exists():
            vehicle = Vehicle.objects.filter(driver=driver).first()
            vehicle.is_approved=False
            vehicle.save()

        return Response({"detail": "Driver profile blocked successfully."}, status=status.HTTP_200_OK)



class UnBlockDriverProfileAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrSuperuser] 

    def post(self, request, *args, **kwargs):
        # Getting data from the request
        # driver_id = kwargs.get('driver_id')
        driver_id = request.data.get("driver_id")
        # Fetch the driver and vehicle instances
        try:
            driver = User.objects.get(id=driver_id, type=User.Types.DRIVER)
        except User.DoesNotExist:
            raise NotFound(detail="Driver not found.")

        
         # UnBlock the driver profile
        driver.profile_status = 'Approve'
        driver.save()
        if Vehicle.objects.filter(driver=driver).exists():
            vehicle = Vehicle.objects.filter(driver=driver).first()
            vehicle.is_approved=True
            vehicle.save()

        return Response({"detail": "Driver profile Unblocked successfully."}, status=status.HTTP_200_OK)


class ApproveDriverProfileAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrSuperuser] 

    def post(self, request, *args, **kwargs):
        # Getting data from the request
        # driver_id = kwargs.get('driver_id')
        driver_id = request.data.get("driver_id")
        # Fetch the driver and vehicle instances
        try:
            driver = User.objects.get(id=driver_id, type=User.Types.DRIVER)
        except User.DoesNotExist:
            raise NotFound(detail="Driver not found.")

         # Approve the driver profile
        driver.profile_status = 'Approve'
        driver.save()
        if Vehicle.objects.filter(driver=driver).exists():
            vehicle = Vehicle.objects.filter(driver=driver).first()
            vehicle.is_approved=True
            vehicle.save()

        return Response({"detail": "Driver profile approve successfully."}, status=status.HTTP_200_OK)

class RejectDriverProfileAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrSuperuser] 

    def post(self, request, *args, **kwargs):
        # Getting data from the request
        driver_id = request.data.get("driver_id")
        # driver_id = kwargs.get('driver_id')
        rejection_reason = request.data.get("rejection_reason", None)
        # Fetch the driver and vehicle instances
        try:
            driver = User.objects.get(id=driver_id, type=User.Types.DRIVER)
        except User.DoesNotExist:
            raise NotFound(detail="Driver not found.")
         # Approve the driver profile
        driver.profile_status = 'Rejected'
        driver.rejection_reason= rejection_reason
        driver.save()
        if Vehicle.objects.filter(driver=driver).exists():
            vehicle = Vehicle.objects.filter(driver=driver).first()
            vehicle.is_approved=False
            vehicle.save()
      

        return Response({"detail": "Driver profile reject successfully."}, status=status.HTTP_200_OK)



from django.utils.timezone import now
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

class AdminDashboardView(APIView):
   def get(self, request, *args, **kwargs):
    # today = now().date()
    today = timezone.localtime().date()
    today_income = Subscription_Logs.objects.filter(subcribe_date__date=today, payment_status='PAID').aggregate(total=Sum('pay_amount'))['total'] or 0
    start_of_week = today - timedelta(days=today.weekday())  # Monday is the start of the week
    this_week_income=Subscription_Logs.objects.filter(subcribe_date__date__gte=start_of_week, payment_status='PAID').aggregate(total=Sum('pay_amount'))['total'] or 0

    start_of_month = today.replace(day=1)
    this_month_income=Subscription_Logs.objects.filter(subcribe_date__date__gte=start_of_month, payment_status='PAID').aggregate(total=Sum('pay_amount'))['total'] or 0
    start_of_year = today.replace(month=1, day=1)
    this_years_income=Subscription_Logs.objects.filter(subcribe_date__date__gte=start_of_year, payment_status='PAID').aggregate(total=Sum('pay_amount'))['total'] or 0
    