from django.urls import path
from couponcode import views

urlpatterns = [
    path('admin/coupons/', views.CoupoListCreateView.as_view(), name='coupon-list-create'),
  
    path('active-coupons/<str:code>/', views.ActiveCouponDetailView.as_view(), name='active-coupon-detail'),
    path('admin/coupon-usage/',views.CouponUsaeListAPIView.as_view(), name='coupon-usage-list'),
]
