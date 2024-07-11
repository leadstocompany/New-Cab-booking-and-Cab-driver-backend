from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Coupon
from .serializers import CouponSerializer, ActiveCouponSerializer
from utility.permissions import IsAdminOrSuperuser
# Create your views here.


class CouponListCreateView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrSuperuser]

class CouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminOrSuperuser]
    lookup_field = 'code'


class ActiveCouponListView(generics.ListAPIView):
    queryset = Coupon.objects.filter(active=True)
    serializer_class = ActiveCouponSerializer
    permission_classes = [permissions.IsAuthenticated]


class ActiveCouponDetailView(generics.RetrieveAPIView):
    queryset = Coupon.objects.filter(active=True)
    serializer_class = ActiveCouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        coupon_code = self.kwargs.get('code')
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            serializer = self.get_serializer(coupon)
            return Response(serializer.data)
        except Coupon.DoesNotExist:
            return Response({'detail': 'Coupon not found'}, status=status.HTTP_404_NOT_FOUND)

