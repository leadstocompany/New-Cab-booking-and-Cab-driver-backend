from django.urls import re_path, include, path

from payment import views
# from payment.views import stripe_webhook


urlpatterns = [
    path('ride-bill-generate/', views.TripBilleGeneratedAPIView.as_view(), name='ride_bill_generate'),
    path('send-ride-payment-request-to-passenger/', views.SendPaymentRequestAPIView.as_view(), name='send-ride-payment-request-to-passenger'),
    path('ride-payment-qrcode-generate/', views.PaymentQRCodeGenerateView.as_view(), name='driver_payment_qrcode-generate'),
    path('create-payment-intent/', views.CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('wallet-payment/', views.WalletPaymentView.as_view(), name='wallet-payment'),
    path('cash-payment/', views.CashPaymentView.as_view(), name='cash-payment'),
    # path('ride/payment/stripe-webhook/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('ride/payment/sucess/', views.UpdateTripPaymentSuccessView.as_view(), name='ride-payment-success'),
    # path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
    path('driver/incomplete-payments/', views.DriverTripIncompletePaymentsView.as_view(), name='driver-incomplete-payments'),
    path('passenger/pending-trip-bill/', views.PassengerTripPendingBilledView.as_view(), name='passenger-pending-trip-bill'),
]