# serializers.py in your users application

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
import secrets
import string

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Check if password is provided, if not generate a random one
        if 'password' not in validated_data or not validated_data['password']:
            validated_data['password'] = make_password(self.generate_password())

        user = User.objects.create_user(**validated_data)
        return user

    @staticmethod
    def generate_password(length=10):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for i in range(length))

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user, created = User.objects.get_or_create(**user_data)
        user_profile, profile_created = UserProfile.objects.get_or_create(user=user, defaults=validated_data)
        if not profile_created:
            # Update the profile if it already exists
            for attr, value in validated_data.items():
                setattr(user_profile, attr, value)
            user_profile.save()
        return user_profile
