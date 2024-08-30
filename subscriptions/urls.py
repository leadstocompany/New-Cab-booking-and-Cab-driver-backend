from django.urls import path
from subscriptions import views

urlpatterns = [
    path('admin/subscription-plans/', views.SubscriptionPlanListCreateView.as_view(), name='subscription-plan-list-create'),
    path('admin/subscription-plans/<int:pk>/', views.SubscriptionPlanDetailView.as_view(), name='subscription-plan-detail'),
    path('admin/subscriptions-logs/', views.SubscriptionsLogsListAPIView.as_view(), name='subscriptions-logs-list'),
    path('admin/subscriptions-log/<int:id>/', views.SubscriptionsLogsUpdateAPIView.as_view(), name='subscriptions-log-update'),
    path('admin/subscriptions/', views.SubscriptionListAPIView.as_view(), name='subscriptions-list'),
    path('admin/active-subscriptions/', views.ActiveSubscriptionListAPIView.as_view(), name='active-subscriptions-list'),
    path('admin/expire-subscriptions/', views.ExpiredSubscriptionListAPIView.as_view(), name='expire-subscriptions-list'),
    path('admin/subscriptions/<int:id>/', views.SubscriptionUpdateAPIView.as_view(), name='subscriptions-update'),
   
    path('subscription-plans/', views.ActiveSubscriptionPlanListView.as_view(), name='subscription-plan'),
    path('subscription/driver/<int:driver_id>/', views.SubscriptionDetailView.as_view(), name='driver-subscription-detail'),
    path('drivers/<int:driver_id>/subscriptions/<int:plan_id>/pay/', views.SubscriptionCreateView.as_view(), name='subscription-pay'),

    path('drivers/<int:driver_id>/subscriptions/<int:plan_id>/payment-intent/pay/', views.SubscriptionPaymentIntentView.as_view(), name='subscription-pay'),

    path('drivers/subscriptions/webhook/', views.DriverSubscriptionStripeWebhookView.as_view(), name='subscriptions-webhook'),

     
]
