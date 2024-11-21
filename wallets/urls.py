from django.urls import path
from wallets import views

urlpatterns = [
    path('create-wallet/', views.CreateWalletView.as_view(), name='create_wallet'),
    path('wallet/', views.GetWalletView.as_view(), name='get_wallet'),
    path('deposit/', views.CreateWalletDepositView.as_view(), name='deposit'),
    path('deposit-success/', views.SuccessWalletDepositView.as_view(), name='deposit-success'),
    path('withdraw/', views.WithdrawView.as_view(), name='withdraw'),
    path('get-transaction-list/', views.GetTransactionView.as_view(), name='transaction-list'),
    
    path('admin/driver/wallets/', views.DriverWalletListView.as_view(), name='driver-wallet-list'),
    path('admin/cutomer/wallets/', views.CustomerWalletListView.as_view(), name='customer-wallet-list'),
    path('admin/users/<int:user_id>/transactions/', views.UserTransactionListView.as_view(), name='user-transactions'),
     # ?date=""
    # ?start_date=""&end_date=""
    path('admin/users/<int:user_id>/wallet/', views.WalletDetailView.as_view(), name='wallet-detail'),
    
] 