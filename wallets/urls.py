from django.urls import path
from wallets import views

urlpatterns = [
    path('create-wallet/', views.CreateWalletView.as_view(), name='create_wallet'),
    path('wallet/', views.GetWalletView.as_view(), name='get_wallet'),
    path('deposit/', views.DepositView.as_view(), name='deposit'),
    path('withdraw/', views.WithdrawView.as_view(), name='withdraw'),
]