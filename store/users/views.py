from django.db import IntegrityError
from rest_framework import generics
from .serializers import UserProfileSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile


class UserCreateView(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except IntegrityError as e:
            if 'phone_number' in str(e):
                return Response({'error': 'This phone number is already in use.'}, status=status.HTTP_400_BAD_REQUEST)
            raise


class UserProfileUpdateView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class TelegramAuthView(APIView):
    def post(self, request):
        telegram_id = request.data.get('telegram_id')

        if telegram_id is None:
            return Response({'error': 'Telegram ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile = UserProfile.objects.get(telegram_id=telegram_id)
            # Здесь можно добавить логику для возвращения токена аутентификации или другой информации о пользователе
            return Response({'message': 'User already exists', 'user_id': user_profile.user.id}, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


class ReferralView(APIView):
    def post(self, request):
        referral_code = request.data.get('referral_code')
        user_telegram_id = request.data.get('telegram_id')

        # Fetching the user profile based on Telegram ID
        try:
            user_profile = UserProfile.objects.get(telegram_id=user_telegram_id)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if referral code exists and is not used by the same user
        try:
            referrer_profile = UserProfile.objects.get(referral_code=referral_code)
            if referrer_profile.user == user_profile.user:
                return Response({'error': 'Cannot use own referral code'}, status=status.HTTP_400_BAD_REQUEST)

            # Award discount
            user_profile.discount += 1000  # Assuming discount is in currency units
            user_profile.save()

            return Response({'message': 'Referral applied successfully', 'discount': user_profile.discount})
        except UserProfile.DoesNotExist:
            return Response({'error': 'Invalid referral code'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    def get(self, request, telegram_id):
        try:
            user_profile = UserProfile.objects.get(telegram_id=telegram_id)
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)