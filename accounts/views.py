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
from admin_api.models import VehicleCertificateField, UserDocumentField
from admin_api.serializers import VehicleCertificateFieldSerializer,UserDocumentFieldSerializer
# Create your views here.


class FileUploadAPI(views.APIView):

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser]
    serializer_class = serializers.FileUploadSerializer

    def post(self, request, format=None, *args, **kwargs):
        serializer = self.serializer_class(
            data={'file': request.data['file'], 'phone': request.user.phone},
            context={'request': request})
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            url = instance.file.url if settings.USE_S3 else f'{settings.SERVER_URL}{instance.file.url}'
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
            return Response(data={"status": False, 'data': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DriverProfileAPI(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.DriverProfileSerializer

    def get_object(self):
        return self.request.user

class GetDriverProfileAPI(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.DriverProfileSerializer

    def get_queryset(self):
        return Driver.objects.filter(is_active=True)


class CustomerProfileAPI(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.CustomerProfileSerializer

    def get_object(self):
        return self.request.user


class DriverResetPasswordAPI(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.DriverResetPasswordSerializer

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

class ActiveUserDocumentFieldList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserDocumentFieldSerializer

    def get_queryset(self):
        return UserDocumentField.objects.filter(active=True)