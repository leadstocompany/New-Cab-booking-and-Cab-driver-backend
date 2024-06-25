
from cabs.models import *
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import Q
from admin_api.serializers import VehicleTypeSerializer, SaveVehicleClassSerializer, VehicleMakerSerializers, SaveVehicleModelSerializer
def save_vehicle_type_view(request):
    if request.user.is_superuser:
        try:
            response=create_vehicle_type(request.data)
            return response
        except Exception as e:
            response={
            'success':'false',
            'status code':status.HTTP_400_BAD_REQUEST,
            'error':str(e)
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
    else:
        response={
            'success':'true',
            'status_code':status.HTTP_200_OK,
            'message':"Admin only create vehicle type"
            }
        status_code=status.HTTP_200_OK
        return JsonResponse(response, status=status_code)
def create_vehicle_type(data):
    serializer = VehicleTypeSerializer(data=data)
    if serializer.is_valid():
        cab_type_name = serializer.validated_data['cab_type']
        if CabType.objects.filter(cab_type=cab_type_name).exists():
            response={
                'success':'false',
                'status code':status.HTTP_200_OK,
                'message':"Cab type already exists."
                }
            return Response(response, status=status.HTTP_200_OK)
        serializer.save()
        response={
            'success':'true',
            'status code':status.HTTP_200_OK,
            'message':"Cab type Add successfully.",
            'data':serializer.data
            }
        return Response(response, status=status.HTTP_201_CREATED)
    response={
        'success':'false',
        'status code':status.HTTP_400_BAD_REQUEST,
        'error':serializer.errors
        }
    return Response(response, status=status.HTTP_400_BAD_REQUEST)

def get_vehicle_type(request):
    if request.user.is_superuser:
        try:
            vehicle_type_obj= CabType.objects.all()
            serializers = VehicleTypeSerializer(vehicle_type_obj, many=True)
            response={
                'success':'true',
                'status_code':status.HTTP_200_OK,
                'data':serializers.data,
            }
            return Response(response, status=status.HTTP_200_OK)
        except vehicle_type_obj.DoesNotExist as e:
            response={
                'success':'false',
                'status_code':status.HTTP_500_INTERNAL_SERVER_ERROR,
                'error':str(e)
            }
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response={
        'success':'true',
        'status_code':status.HTTP_200_OK,
        'message':"Admin only create vehicle type"
        }
        status_code=status.HTTP_200_OK
        return JsonResponse(response, status=status_code)
    
def save_vehicle_class_view(request):
    try:
        if request.user.is_superuser:
            response=create_vehicle_class(request.data)
            return response
        else:
            response={
                'success':'true',
                'status_code':status.HTTP_200_OK,
                'message':"Admin only create vehicle class"
                }
            status_code=status.HTTP_200_OK
            return JsonResponse(response, status=status_code)
    except Exception as e:
        response={
            'success':'false',
            'status code':status.HTTP_400_BAD_REQUEST,
            'error':str(e)
            }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
def create_vehicle_class(data):
    serializer = SaveVehicleClassSerializer(data=data)
    serializer.is_valid(raise_exception=True)  # Trigger Bad Request if errors exist
    cab_class_name = serializer.validated_data['cab_class']
    cab_type=CabType.objects.get(id=data["cab_type"])
    if CabClass.objects.filter(cab_class=cab_class_name).exists():
        response={
            'success':'false',
            'status code':status.HTTP_200_OK,
            'message':"Cab class already exists."
            }
        return Response(response, status=status.HTTP_200_OK)
    serializer.save()         # Passing the current user
    response={
        'success':'True',
        'status code':status.HTTP_201_CREATED,
        'message':"Cab class Add Successfully.",
        'data':serializer.data
    }
    return Response(response, status=status.HTTP_201_CREATED)

def save_vehicle_maker_view(request):
    if request.user.is_superuser:
        try:
            response=create_vehicle_maker(request.data)
            return response
        except Exception as e:
            response={
            'success':'false',
            'status code':status.HTTP_400_BAD_REQUEST,
            'error':str(e)
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
    else:
        response={
            'success':'true',
            'status_code':status.HTTP_200_OK,
            'message':"Admin only create vehicle maker"
            }
        status_code=status.HTTP_200_OK
        return JsonResponse(response, status=status_code)

def create_vehicle_maker(data):
    serializer = VehicleMakerSerializers(data=data)
    if serializer.is_valid():
        maker_name = serializer.validated_data['maker']
        if VehicleMaker.objects.filter(maker=maker_name).exists():
            response={
                'success':'false',
                'status code':status.HTTP_200_OK,
                'message':"Vehicle Maker already exists."
                }
            return Response(response, status=status.HTTP_200_OK)
        serializer.save()
        response={
            'success':'true',
            'status code':status.HTTP_200_OK,
            'message':"Vehicle Maker Add successfully.",
            'data':serializer.data,
            }
        return Response(response, status=status.HTTP_201_CREATED)
    response={
        'success':'false',
        'status code':status.HTTP_400_BAD_REQUEST,
        'error':serializer.errors
        }
    return Response(response, status=status.HTTP_400_BAD_REQUEST)

def get_vehicle_maker_view(request):
    if request.user.is_superuser:
        try:
            vehicle_maker_obj= VehicleMaker.objects.all()
            serializers = VehicleMakerSerializers(vehicle_maker_obj, many=True)
            response={
                'success':'true',
                'status_code':status.HTTP_200_OK,
                'data':serializers.data,
            }
            return Response(response, status=status.HTTP_200_OK)
        except vehicle_maker_obj.DoesNotExist as e:
            response={
                'success':'false',
                'status_code':status.HTTP_500_INTERNAL_SERVER_ERROR,
                'error':str(e)
            }
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response={
        'success':'true',
        'status_code':status.HTTP_200_OK,
        'message':"Admin only create vehicle type"
        }
        status_code=status.HTTP_200_OK
        return JsonResponse(response, status=status_code)

# def save_vehicle_model_view(request):
#     try:
#         if request.user.is_superuser:
#             response=create_vehicle_model(request.data)
#             return response
#         else:
#             response={
#                 'success':'true',
#                 'status_code':status.HTTP_200_OK,
#                 'message':"Admin only create vehicle class"
#                 }
#             status_code=status.HTTP_200_OK
#             return JsonResponse(response, status=status_code)
#     except Exception as e:
#         response={
#             'success':'false',
#             'status code':status.HTTP_400_BAD_REQUEST,
#             'error':str(e)
#             }
#         return Response(response, status=status.HTTP_400_BAD_REQUEST)
# def create_vehicle_model(data):
#     serializer = SaveVehicleModelSerializer(data=data)
#     serializer.is_valid(raise_exception=True)  # Trigger Bad Request if errors exist
#     vehicle_model_name = serializer.validated_data['model']
#     # vehicle_maker=VehicleMaker.objects.get(id=data["maker_id"])
#     if VehicleModel.objects.filter(model=vehicle_model_name).exists():
#         response={
#             'success':'false',
#             'status code':status.HTTP_200_OK,
#             'message':"vehicle model already exists."
#             }
#         return Response(response, status=status.HTTP_200_OK)
#     serializer.save()         # Passing the current user
#     response={
#         'success':'false',
#         'status code':status.HTTP_201_CREATED,
#         'message':"vehilce model Add Successfully.",
#         'data':serializer.data,
#     }
#     return Response(response, status=status.HTTP_201_CREATED)



 