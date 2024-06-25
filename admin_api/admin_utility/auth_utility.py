
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from accounts.models import *
from trips.models import Trip
from cabs.models import *
from rest_framework import status

def admin_login_view(serializer, data):
    try:
        if serializer.is_valid():
            username = data.get('username')
            if '@' in username:
                admin = User.objects.get(email =username)
            else:
                admin = User.objects.get(phone=username)
            token, _ = Token.objects.get_or_create(user=admin)
            response = {
                'success' : 'true',
                'status code' : status.HTTP_200_OK,
                'message': 'Admin logged in successfully',
                'admin_id':admin.id,
                'is_superuser':admin.is_superuser,
                'first_name':admin.first_name,
                'last_name':admin.last_name,
                'email':admin.email,
                'phone':admin.phone,
                'profile_photo':admin.photo_upload,
                'token': token.key,
                }
            status_code = status.HTTP_200_OK
            return Response(response, status=status_code)
        else:
            response = {
            'success' : 'false',
            'status code' : status.HTTP_400_BAD_REQUEST,
            'message': 'invalid Credintials',
            'error': 'email,mobile,password not found',
            }
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(response, status=status_code)
    except Exception as e:
        print(e, 'e')
        response = {
            'success' : 'false',
            'status code' : status.HTTP_400_BAD_REQUEST,
            'message': 'invalid Credintials',
            'error': e,
            }
        status_code = status.HTTP_400_BAD_REQUEST
        return Response(response, status=status_code)

def logout_view(request):
    request.auth.delete()
    response = {
        'success' : 'true',
        'status code' : status.HTTP_204_NO_CONTENT,
        'message': 'Admin logout successfully',
        }
    status_code = status.HTTP_204_NO_CONTENT
    return Response(response, status=status_code)


