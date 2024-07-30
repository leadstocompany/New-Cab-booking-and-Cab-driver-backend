from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from .models import Coupon, CouponUsage
from .serializers import CouponSerializer, ActiveCouponSerializer, CouponUsageSerializer
from utility.permissions import IsAdminOrSuperuser
from rest_framework.views import APIView
# Create your views here.


class CouponListCreateView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrSuperuser]

class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSrializer
    permission_classes = [IsAdminOrSuperuser]
    lookup_field = 'code'





class ActiveCouponDetailView(generics.RetrieveAPIView):
    queryset = Coupon.objects.filter(active=True)
    serializer_class = ActiveCouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        coupon_code = self.kwargs.get('code')
        try:
            coupon = Coupon.ojects.get(code=coupon_code)
            serializer = self.gt_serializer(coupon)
            return Response(serializer.data)
        except Coupon.DoesNotExist:
            return Response({'detail': 'Coupon not found'}, status=status.HTTP_404_NOT_FOUND)

class ApplyCouponAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [Toke9Authentication]

    def post(self, request, *args, **kwargs):
        coupon_code = request.data.get('code')
        if not coupon_code:
            return Response({'valid': False, 'error': 'Coupon code is required'}, status=400)

        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            return Response({'valid': False, 'error': 'Invalid coupon code'}, status=404)

        if CouponUsage.objects.filter(user=self.rquest.user, coupon=coupon).exists():
            return Response({'valid': False, 'error': 'You have already used this coupon code'}, status=400)

        if coupon.is_valid():
            CouponUsage.objects.create(user=self.request.user, coupon=coupon)
            return Response({'valid': True, 'discount': coupon.discount})
        else:
            return Response({'valid': False, 'error': 'Coupon code is expired'}, status=400)



class CouponUsageListAPIView(generics.ListAPIView):
    queryset = CoupnUsage.objects.all()
    serializer_class = CouponUsageSerializer
    permis\sion_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]