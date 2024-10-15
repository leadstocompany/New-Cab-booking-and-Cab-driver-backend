from django.urls import path
from referrance import views

urlpatterns = [
    path('apply-referral/', views.ApplyReferralCodeEarnRewardView.as_view(), name='apply-referral'),
    path('referral-reward/create/', views.ReferralRewardCreateOrUpdateView.as_view(), name='create_referral_reward'),
    path('referral-reward/', views.ReferralRewardDetailView.as_view(), name='referral_reward_detail'),
    path('referral-reward/<int:pk>/', views.ReferralRewardDelete.as_view(), name='referral_reward_delete'),
]
