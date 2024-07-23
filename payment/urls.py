from django.urls import re_path, include, path

from payment import views
# from payment.views import stripe_webhook


urlpatterns = [
   
    path('driver-payment-request/', views.PaymentRequestView.as_view(), name='driver_payment_request'),
    path('create-payment-intent/', views.CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('wallet-payment/', views.WalletPaymentView.as_view(), name='wallet-payment'),
    path('cash-payment/', views.CashPaymentView.as_view(), name='cash-payment'),
    path('stripe-webhook/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    # path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
]