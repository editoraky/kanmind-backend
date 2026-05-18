from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from auth_app.api.serializers import RegistrationSerializer, LoginSerializer, UserSerializer
from auth_app.models import User


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = Token.objects.create(user=user)

        data = {
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.id,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token, _ = Token.objects.get_or_create(user=user)

        data = {
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.id,
        }
        return Response(data, status=status.HTTP_200_OK)


class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')

        if not email:
            return Response(
                {'error': 'Email-Parameter fehlt.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(email=email).first()
        if user is None:
            return Response(
                {'error': 'Email nicht gefunden.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)