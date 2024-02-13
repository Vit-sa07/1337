from django.urls import path
from .views import UserCreateView, UserProfileUpdateView, TelegramAuthView, ReferralView, UserProfileView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('update-profile/', UserProfileUpdateView.as_view(), name='user-update-profile'),
    path('telegram-auth/', TelegramAuthView.as_view(), name='telegram-auth'),
    path('referral/', ReferralView.as_view(), name='referral'),
    path('profile/<int:telegram_id>/', UserProfileView.as_view(), name='user-profile'),
]
