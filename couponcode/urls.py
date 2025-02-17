from django.urls import path
from couponcode import views

urlpatterns = [
    path('admin/coupons/', views.CouponListCreateView.as_view(), name='coupon-list-create'),
    path('admin/coupons/<str:code>/', views.CouponDetailView.as_view(), name='coupon-detail'),
    path('active-coupons/', views.ActiveCouponListView.as_view(), name='active-coupons-list'),
    path('active-coupons/<str:code>/', views.ActiveCouponDetailView.as_view(), name='active-coupon-detail'),
    path('admin/coupons/delete/<str:code>/', views.CouponDestroyView.as_view(), name='coupon-delete'),
    path('apply-coupon-code/', views.ApplyCouponAPI.as_view()),
    path('admin/coupon-usage/',views.CouponUsageListAPIView.as_view(), name='coupon-usage-list')
]
