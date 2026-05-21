from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationDuplicateEmailTests(APITestCase):
    def setUp(self):
        self.existing_user = User.objects.create_user(
            email='test@yasef.de',
            fullname='Existing User',
            password='geheim123',
        )
        self.url = '/api/registration/'

    def _payload(self, **overrides):
        data = {
            'fullname': 'New User',
            'email': 'test@yasef.de',
            'password': 'geheim123',
            'repeated_password': 'geheim123',
        }
        data.update(overrides)
        return data

    def test_returns_400_when_email_already_registered(self):
        response = self.client.post(self.url, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)