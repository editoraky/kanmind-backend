"""Serializers for user registration, login and lightweight user lookups."""

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from auth_app.models import User
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration input and create a new ``User`` from it."""

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        """Serializer configuration mapping fields to the ``User`` model."""

        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        """Ensure the password and its confirmation match before saving."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        """Create the user via the manager so the password is hashed."""
        validated_data.pop('repeated_password')
        user = User.objects.create_user(fullname=validated_data['fullname'], email=validated_data['email'], password=validated_data['password'])
        return user


class LoginSerializer(serializers.Serializer):
    """Validate email/password credentials and expose the authenticated user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the supplied credentials and attach the user to ``attrs``."""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError('Invalid login credentials.')

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Minimal user representation used as a nested or lookup payload."""

    class Meta:
        """Expose only public-safe fields of the user."""

        model = User
        fields = ['id', 'email', 'fullname']

