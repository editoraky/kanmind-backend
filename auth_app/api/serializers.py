from rest_framework import serializers
from auth_app.models import User

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError("Passwörter stimmen nicht überein.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        user = User.objects.create_user(fullname=validated_data['fullname'], email=validated_data['email'], password=validated_data['password'])
        return user