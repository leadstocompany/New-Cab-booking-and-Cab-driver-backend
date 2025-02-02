import pyotp
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, parsers, permissions, status, views
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from accounts import serializers
from accounts.models import *
from utility.otp import send_otp
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.conf import settings
from admin_api.models import VehicleCertificateField, UserDocumentField, VehiclePhotoPage, City
from admin_api.serializers import  CitySerializer, VehicleCertificateFieldSerializer,UserDocumentFieldSerializer, VehiclePhotoPageSerializer
from rest_framework import viewsets
from accounts.serializers import *
from rest_framework.views import APIView
from JLP_MyRide import settings
from django.db.models import Sum, Count
from dateutil.relativedelta import relativedelta
import logging
logger = logging.getLogger(__name__)
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.


class FileUploadAPI(views.APIView):

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser]
    serializer_class = FileUploadSerializer

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(
            data={'file': request.data['file'], 'phone': request.user.phone},
            context={'request': request})
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
           
            url = f'{settings.SERVER_URL}{instance.file.url}'
            print("url")

            return Response({"url": url}, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class DriverRegisterAPI(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone", None)

        try:
            if User.objects.filter(phone=phone).exists():
                print("JLP")
                return Response(data={"status": False, 'data': "Number already registered"}, status=status.HTTP_400_BAD_REQUEST)

            driver = Driver.objects.create(phone=phone, code=create_ref_code())
            hotp = pyotp.HOTP(driver.hash(), 4)
            send_otp(hotp.at(driver.driverphoneverify.count), driver.phone)
            return Response(data={"status": True}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response(data={"status": False, 'data': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DriverLoginAPI(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone", None)

        try:
            if User.objects.filter(phone=phone).exists():
                driver = Driver.objects.filter(phone=phone).first()
                hotp = pyotp.HOTP(driver.hash(), 4)
               
                driverphoneverify = driver.driverphoneverify
                driverphoneverify.count += 1
                driverphoneverify.save()
                send_otp(hotp.at(driverphoneverify.count), driver.phone)
                return Response(data={"status": True}, status=status.HTTP_200_OK)
            else:
                driver = Driver.objects.create(phone=phone, code=create_ref_code())
                hotp = pyotp.HOTP(driver.hash(), 4)
                send_otp(hotp.at(driver.driverphoneverify.count), driver.phone)
                return Response(data={"status": True}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response(data={"status": False, 'data': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DriverOTPVerifyLoginAPI(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone", None)
        otp = request.data.get("otp", None)
        try:
            if not Driver.objects.filter(phone=phone).exists():
                return Response(data={"status": False, 'data': "Phone Number not registered"}, status=status.HTTP_400_BAD_REQUEST)
            driver = Driver.objects.filter(phone=phone).first()
            print(driver.code)
            hotp = pyotp.HOTP(driver.hash(), 4)
            phone_obj = driver.driverphoneverify
            if otp and phone:
                # if str(otp) == hotp.at(phone_obj.count):
                if str(otp) == "1234":
                    token, _ = Token.objects.get_or_create(user=driver)
                    print(Token.objects.get_or_create(user=driver)[0].__dict__)
                    return Response(data={"status": True, "token":token.key}, status=status.HTTP_201_CREATED)
                else:
                    return Response(data={"status": False, 'data': "Phone OTP is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

            phone_obj.count += 1
            phone_obj.save()

            send_otp(hotp.at(driver.driverphoneverify.count), driver.phone)
            return Response(data={"status": True, }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response(data={"status": False, 'data': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CustomerRegisterAPI(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone", None)
        referrer = request.data.get("referrer", None)

        try:
            if User.objects.filter(phone=phone).exists():
                print("JLP")
                return Response(data={"status": False, 'data': "Number already registered"}, status=status.HTTP_400_BAD_REQUEST)
            customer = Customer.objects.create(
                phone=phone, code=create_ref_code())

            CustomerPhoneVerify.objects.get_or_create(user=customer)
            if phone and referrer:
                if not Customer.objects.filter(code=referrer).exists():
                    return Response(data={"status": False, 'data': "referrel code donesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
                # referral
                referred = Customer.objects.filter(code=referrer).first()
                customer_ref = CustomerReferral.objects.create(
                    referred=referred, referrer=customer)
                print(customer_ref)

            hotp = pyotp.HOTP(customer.hash(), 4)
            send_otp(hotp.at(customer.customerphoneverify.count), customer.phone)
            return Response(data={"status": True}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response(data={"status": False, 'data': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginCustomerwithPhoneNumberApi(views.APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        try:
            phone = request.data.get("phone", None)
            if phone:
                if not User.objects.filter(phone=phone).exists():
                    customer = Customer.objects.create(phone=phone, code=create_ref_code())
                    hotp = pyotp.HOTP(customer.hash(), 4)
                    customerphoneverify = customer.customerphoneverify
                    send_otp(hotp.at(customerphoneverify.count), customer.phone)
                    return Response(data={"status": True, "phone":customer.phone}, status=status.HTTP_201_CREATED)
                    # return Response(data={"status": False, 'data': "User not exist"}, status=status.HTTP_400_BAD_REQUEST)
                
                customer = Customer.objects.get(phone=phone)
                hotp = pyotp.HOTP(customer.hash(), 4)
                customerphoneverify = customer.customerphoneverify
                customerphoneverify.count += 1
                customerphoneverify.save()
                send_otp(hotp.at(customerphoneverify.count), customer.phone)
                return Response(data={"status": True, "phone":customer.phone}, status=status.HTTP_200_OK)
            
            else:
                return Response(data={"status": False, 'data': "Login Failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response(data={"status": False, 'data': str(e)}, status=status.HTTP_400_BAD_REQUEST) 
class CustomerOtpVerifyLoginAPI(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone", None)
        otp = request.data.get("otp", None)
        try:
            if not Customer.objects.filter(phone=phone).exists():
                return Response(data={"status": False, 'data': "Phone Number not registered"}, status=status.HTTP_400_BAD_REQUEST)
            customer = Customer.objects.filter(phone=phone).first()
            hotp = pyotp.HOTP(customer.hash(), 4)
            phone_obj = customer.customerphoneverify
            if otp and phone:
                # if str(otp) == hotp.at(phone_obj.count):
                if str(otp) == "1234":
                    token, _ = Token.objects.get_or_create(user=customer)
                    return Response(data={"status": True, "user_id":customer.id,"token": token.key}, status=status.HTTP_201_CREATED)
                else:
                    return Response(data={"status": False, 'data': "Phone OTP is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

            phone_obj.count += 1
            phone_obj.save()

            send_otp(hotp.at(customer.customerphoneverify.count), customer.phone)
            return Response(data={"status": True, }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response(data={"status": False, 'data': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DriverProfileAPI(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DriverProfileSerializer

    def get_object(self):
        return self.request.user

class GetDriverProfileAPI(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DriverProfileSerializer

    def get_queryset(self):
        return Driver.objects.filter(is_active=True)


class CustomerProfileAPI(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class =CustomerProfileSerializer

    def get_object(self):
        return self.request.user


class DriverResetPasswordAPI(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DriverResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = self.request.user
            print(user.password)
            user.password = make_password(
                serializer.validated_data['password'])
            user.save()
            print(user.password)
            return Response({"status": True, }, status=status.HTTP_200_OK)


class ActiveVehicleCertificateFieldList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VehicleCertificateFieldSerializer

    def get_queryset(self):
        return VehicleCertificateField.objects.filter(active=True)
    
class ActiveVehiclePhotoPageList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VehiclePhotoPageSerializer

    def get_queryset(self):
        return VehiclePhotoPage.objects.filter(active=True)

class ActiveUserDocumentFieldList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserDocumentFieldSerializer

    def get_queryset(self):
        return UserDocumentField.objects.filter(active=True)


# class BankAccountCreateAPIView(generics.CreateAPIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     queryset = BankAccount.objects.all()
#     serializer_class = BankAccountSerializer

class BankAccountCreateAPIView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    
    def create(self, request, *args, **kwargs):
        # Generate or modify account_id
        # Create a mutable copy of the request data
        data = request.data
        # Update the account_id field
        try:
            bank_account = stripe.Token.create(
                bank_account={
                    "country": "US",
                    "currency": "usd",
                    "account_holder_name": data['name'],
                    "account_holder_type": "individual",  # Or "company"
                    "routing_number": data['routing_number'],
                    "account_number": data['account_number'],
                },
            )
            external_account = stripe.Account.create_external_account(
                "acct_1PR5HtICrH978laK",  # Replace with your admin's Stripe account ID
                external_account=bank_account.id
                )
            data['account_id'] = external_account.id
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            pass

        # Validate and save the object using the serializer
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Return the serialized data with the updated account_id field
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class DriverBankAccountAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, format=None):
        try:
            driver_id = request.user.id
            bank_account = BankAccount.objects.get(driver__id=driver_id)
            serializer = BankAccountSerializer(bank_account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BankAccount.DoesNotExist as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Bank account not found for this driver."}, status=status.HTTP_404_NOT_FOUND)



class UpdateDriverBankAccountAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get_object(self, driver_id):
        try:
            return BankAccount.objects.get(driver__id=driver_id)
        except BankAccount.DoesNotExist:
            return None
    def patch(self, request,format=None):
        driver_id = request.user.id
        bank_account_detail = self.get_object(driver_id)
        if not bank_account_detail:
            return Response({"error": "Bank account not found for this driver."}, status=status.HTTP_404_NOT_FOUND)
        try:
            if bank_account_detail.account_id:
                stripe.Account.delete_external_account(
                    "acct_ADMIN_ACCOUNT_ID",  # Replace with your admin's Stripe account ID
                    bank_account_detail.account_id
                )
            account_token = stripe.Token.create(
                 bank_account={
                    "country": "US",
                    "currency": "usd",
                    "account_holder_name": request.data['name'],
                    "account_holder_type": "individual",  # Or "company"
                    "routing_number": request.data['routing_number'],
                    "account_number": request.data['account_number'],
                },
            )
            external_account = stripe.Account.create_external_account(
                "acct_ADMIN_ACCOUNT_ID",  # Admin's Stripe account ID
                external_account=account_token.id
            )
            request.data['account_id'] = external_account.id

        except Exception as e:
            logger.error(f"Error occurred: {e}")
            pass

        serializer = BankAccountSerializer(bank_account_detail, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class CurrentUserLocationView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         current_location, created = CurrentLocation.objects.get_or_create(user=request.user)
#         serializer = CurrentLocationSerializer(current_location)
#         return Response(serializer.data)

#     def put(self, request):
#         current_location, created = CurrentLocation.objects.get_or_create(user=request.user)
#         serializer = CurrentLocationSerializer(current_location, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)


# class CurrentLocationCreateView(generics.CreateAPIView):
#     queryset = CurrentLocation.objects.all()
#     serializer_class = CurrentLocationSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_create(self, serializer):
#         user = self.request.user
#         serializer.save(user=user)

# class CurrentLocationUpdateView(generics.UpdateAPIView):
#     queryset = CurrentLocation.objects.all()
#     serializer_class = CurrentLocationSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = 'user_id'

#     def get_object(self):
#         user = self.request.user
#         return CurrentLocation.objects.get(user=user)

# class CurrentLocationDetailView(generics.RetrieveAPIView):
#     queryset = CurrentLocation.objects.all()
#     serializer_class = CurrentLocationSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = 'user_id'

#     def get_object(self):
#         user = self.request.user
#         return CurrentLocation.objects.get(user=user)
from django.utils import timezone
class CurrentLocationAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        user = request.user
        latitude = request.data.get('current_latitude')
        longitude = request.data.get('current_longitude')

        if not latitude or not longitude:
            return Response({"error": "Latitude and Longitude are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            location = CurrentLocation.objects.get(user=user)
            location.current_latitude = latitude
            location.current_longitude = longitude
            location.timestamp=timezone.localtime(timezone.now())
            location.save()
            serializer = CurrentLocationSerializer(location)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CurrentLocation.DoesNotExist:
            location = CurrentLocation.objects.create(user=user, current_latitude=latitude, current_longitude=longitude)
            serializer = CurrentLocationSerializer(location)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ActiveCityListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CitySerializer

    def get_queryset(self):
        return City.objects.filter(active=True)


class SaveFCMTokenView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        try:
            fcm_token = request.data.get('fcm_token')
            if fcm_token:
                user=User.objects.get(id=request.user.id)
                user.fcm_token=fcm_token
                user.save()
                return Response({"fcm_token":user.fcm_token}, status=status.HTTP_200_OK)
            else:
                return Response({"error":"fcm_token field required"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   

class DriverDutyOnOffView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        try:
            driver_duty = request.data.get('driver_duty')
            if driver_duty:
                driver=Driver.objects.get(id=request.user.id)
                driver.driver_duty=driver_duty
                driver.save()
                return Response({"id":driver.id, "driver_duty":driver.driver_duty}, status=status.HTTP_200_OK)
            else:
                return Response({"error":"driver_duty field required"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   


class DriverAnalyticsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        driver = request.user
        month = request.query_params.get('month')
        
        # Base query for completed trips
        base_query = Trip.objects.filter(
            driver=driver,
            status='COMPLETED',
            payment_status='paid'
        )

        if month:
            # Filter for specific month
            base_query = base_query.filter(
                ride_end_time__month=month,
                ride_end_time__year=timezone.now().year
            )
        else:
            # Get last 6 months data
            six_months_ago = timezone.now() - relativedelta(months=6)
            base_query = base_query.filter(ride_end_time__gte=six_months_ago)

        # Calculate metrics
        total_rides = base_query.count()
        total_income = base_query.aggregate(Sum('total_fare'))['total_fare__sum'] or 0
        total_distance = base_query.aggregate(Sum('distance'))['distance__sum'] or 0

        # Get month-wise breakdown
        monthly_data = []
        for i in range(6):
            month_date = timezone.now() - relativedelta(months=i)
            month_stats = base_query.filter(
                ride_end_time__month=month_date.month,
                ride_end_time__year=month_date.year
            ).aggregate(
                rides=Count('id'),
                income=Sum('total_fare'),
                distance=Sum('distance')
            )
            
            monthly_data.append({
                'month_name': month_date.strftime('%B %Y'),
                'month': month_date.month,
                'year': month_date.year,
                'rides': month_stats['rides'] or 0,
                'income': month_stats['income'] or 0,
                'distance': month_stats['distance'] or 0
            })

        response_data = {
            'total_rides': total_rides,
            'total_income': total_income,
            'total_distance': total_distance,
            'monthly_breakdown': monthly_data
        }

        return Response(response_data)