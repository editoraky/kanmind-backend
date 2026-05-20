from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model

from kanban_app.models import Board

User = get_user_model()


class BoardDetailTests(APITestCase):
    def setUp(self):
        self.yasef = User.objects.create_user(
            email='test@yasef.de',
            fullname='Yasef',
            password='geheim123',
        )
        self.user2 = User.objects.create_user(
            email='test2@yasef.de',
            fullname='User Two',
            password='geheim123',
        )

        self.token_yasef = Token.objects.create(user=self.yasef)
        self.token_user2 = Token.objects.create(user=self.user2)

        self.board_owner = Board.objects.create(
            title='Yasef Owner Board',
            owner=self.yasef,
        )
        self.board_member = Board.objects.create(
            title='User2 Board mit Yasef als Member',
            owner=self.user2,
        )
        self.board_member.members.add(self.yasef)

        self.board_stranger = Board.objects.create(
            title='User2 Solo Board',
            owner=self.user2,
        )

    def test_returns_401_when_no_token(self):
        url = f'/api/boards/{self.board_owner.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_404_when_board_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        url = '/api/boards/99999/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_200_when_user_is_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        url = f'/api/boards/{self.board_owner.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.board_owner.id)
        self.assertEqual(response.data['title'], 'Yasef Owner Board')
        self.assertEqual(response.data['owner_id'], self.yasef.id)
        self.assertEqual(response.data['members'], [])
        self.assertEqual(response.data['tasks'], [])

    def test_returns_200_when_user_is_member(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        url = f'/api/boards/{self.board_member.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['owner_id'], self.user2.id)
        self.assertEqual(len(response.data['members']), 1)
        member = response.data['members'][0]
        self.assertEqual(member['id'], self.yasef.id)
        self.assertEqual(member['email'], 'test@yasef.de')
        self.assertEqual(member['fullname'], 'Yasef')

    def test_returns_403_when_user_is_stranger(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        url = f'/api/boards/{self.board_stranger.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)