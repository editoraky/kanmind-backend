from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model

from kanban_app.models import Board, Task, Comment

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

    def test_patch_returns_401_when_no_token(self):
        url = f'/api/boards/{self.board_owner.id}/'
        response = self.client.patch(url, {'title': 'Egal'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_returns_404_when_board_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        url = '/api/boards/99999/'
        response = self.client.patch(url, {'title': 'Egal'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_returns_403_when_user_is_stranger(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        url = f'/api/boards/{self.board_stranger.id}/'
        response = self.client.patch(url, {'title': 'Egal'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_returns_200_and_updates_title_when_user_is_owner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        url = f'/api/boards/{self.board_owner.id}/'

        response = self.client.patch(url, {'title': 'Neuer Titel'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.board_owner.id)
        self.assertEqual(response.data['title'], 'Neuer Titel')
        self.assertEqual(response.data['owner_data']['id'], self.yasef.id)
        self.assertEqual(response.data['owner_data']['email'], 'test@yasef.de')
        self.assertEqual(response.data['members_data'], [])

        self.board_owner.refresh_from_db()
        self.assertEqual(self.board_owner.title, 'Neuer Titel')

    def test_patch_returns_200_when_user_is_member(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        url = f'/api/boards/{self.board_member.id}/'
        response = self.client.patch(url, {'title': 'Member Update'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Member Update')

    def test_patch_does_not_change_unspecified_fields(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        url = f'/api/boards/{self.board_member.id}/'
        original_title = self.board_member.title

        response = self.client.patch(
            url,
            {'members': [self.user2.id]},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.board_member.refresh_from_db()
        self.assertEqual(self.board_member.title, original_title)

    def test_delete_returns_401_when_no_token(self):
        url = f'/api/boards/{self.board_owner.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_returns_404_when_board_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        url = '/api/boards/99999/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_returns_403_when_user_is_stranger(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        url = f'/api/boards/{self.board_stranger.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_returns_403_when_user_is_member(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        url = f'/api/boards/{self.board_member.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_returns_204_and_cascades_when_user_is_owner(self):
        task = Task.objects.create(
            board=self.board_owner,
            title='Cascade Test Task',
            creator=self.yasef,
        )
        comment = Comment.objects.create(
            task=task,
            author=self.yasef,
            content='Cascade Test Comment',
        )
        board_id = self.board_owner.id
        task_id = task.id
        comment_id = comment.id

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')
        response = self.client.delete(f'/api/boards/{board_id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Board.objects.filter(pk=board_id).exists())
        self.assertFalse(Task.objects.filter(pk=task_id).exists())
        self.assertFalse(Comment.objects.filter(pk=comment_id).exists())

class TaskCreateTests(APITestCase):
    def setUp(self):
        self.yasef = User.objects.create_user(
            email='test@yasef.de',
            fullname='Yasef',
            password='geheim123',
        )
        self.member = User.objects.create_user(
            email='member@yasef.de',
            fullname='Member',
            password='geheim123',
        )
        self.outsider = User.objects.create_user(
            email='outsider@yasef.de',
            fullname='Outsider',
            password='geheim123',
        )
        self.token_yasef = Token.objects.create(user=self.yasef)

        self.board = Board.objects.create(title='Test Board', owner=self.yasef)
        self.board.members.add(self.member)

        self.board_stranger = Board.objects.create(
            title='Stranger Board',
            owner=self.outsider,
        )

        self.url = '/api/tasks/'

    def _auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token_yasef.key}')

    def _valid_payload(self, **overrides):
        payload = {
            'board': self.board.id,
            'title': 'Test Task',
            'description': 'A test',
            'status': 'to-do',
            'priority': 'medium',
            'due_date': '2026-12-31',
        }
        payload.update(overrides)
        return payload

    def test_create_returns_401_when_no_token(self):
        response = self.client.post(self.url, self._valid_payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_returns_404_when_board_does_not_exist(self):
        self._auth()
        response = self.client.post(
            self.url,
            self._valid_payload(board=99999),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_returns_403_when_user_is_stranger(self):
        self._auth()
        response = self.client.post(
            self.url,
            self._valid_payload(board=self.board_stranger.id),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_returns_400_when_title_missing(self):
        self._auth()
        payload = self._valid_payload()
        del payload['title']
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_returns_400_when_assignee_is_not_board_member(self):
        self._auth()
        response = self.client.post(
            self.url,
            self._valid_payload(assignee_id=self.outsider.id),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('assignee_id', response.data)

    def test_create_returns_400_when_reviewer_is_not_board_member(self):
        self._auth()
        response = self.client.post(
            self.url,
            self._valid_payload(reviewer_id=self.outsider.id),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('reviewer_id', response.data)

    def test_create_returns_201_with_nested_response_when_owner(self):
        self._auth()
        payload = self._valid_payload(
            assignee_id=self.member.id,
            reviewer_id=self.yasef.id,
        )
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Task')
        self.assertEqual(response.data['assignee']['id'], self.member.id)
        self.assertEqual(response.data['reviewer']['id'], self.yasef.id)
        self.assertEqual(response.data['comments_count'], 0)
        self.assertNotIn('assignee_id', response.data)

    def test_create_sets_creator_to_request_user(self):
        self._auth()
        response = self.client.post(self.url, self._valid_payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(pk=response.data['id'])
        self.assertEqual(task.creator, self.yasef)

    def test_create_returns_201_when_user_is_board_member(self):
        token_member = Token.objects.create(user=self.member)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token_member.key}')
        response = self.client.post(self.url, self._valid_payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class TaskUpdateTests(APITestCase):
    def setUp(self):
        self.yasef = User.objects.create_user(
            email='yasef@example.com',
            fullname='Yasef',
            password='geheim123',
        )
        self.member = User.objects.create_user(
            email='member@example.com',
            fullname='Member',
            password='geheim123',
        )
        self.outsider = User.objects.create_user(
            email='outsider@example.com',
            fullname='Outsider',
            password='geheim123',
        )
        self.token_yasef = Token.objects.create(user=self.yasef)
        self.token_member = Token.objects.create(user=self.member)
        self.token_outsider = Token.objects.create(user=self.outsider)
        self.board = Board.objects.create(title='Board', owner=self.yasef)
        self.board.members.add(self.member)
        self.task = Task.objects.create(
            board=self.board,
            creator=self.yasef,
            title='Task',
            status='to-do',
            priority='medium',
        )

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def _patch(self, task_id, payload):
        return self.client.patch(f'/api/tasks/{task_id}/', payload, format='json')

    def test_patch_returns_401_when_no_token(self):
        response = self._patch(self.task.id, {'title': 'Neu'})
        self.assertEqual(response.status_code, 401)

    def test_patch_returns_404_when_task_does_not_exist(self):
        self._auth(self.token_yasef)
        response = self._patch(999999, {'title': 'Neu'})
        self.assertEqual(response.status_code, 404)

    def test_patch_returns_403_when_user_is_stranger(self):
        self._auth(self.token_outsider)
        response = self._patch(self.task.id, {'title': 'Neu'})
        self.assertEqual(response.status_code, 403)

    def test_patch_returns_200_when_user_is_board_owner(self):
        self._auth(self.token_yasef)
        response = self._patch(self.task.id, {'title': 'Neu'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Neu')

    def test_patch_returns_200_when_user_is_board_member(self):
        self._auth(self.token_member)
        response = self._patch(self.task.id, {'title': 'Neu'})
        self.assertEqual(response.status_code, 200)

    def test_patch_ignores_board_field_when_attempted(self):
        other_board = Board.objects.create(title='Other', owner=self.yasef)
        self._auth(self.token_yasef)
        response = self._patch(
            self.task.id,
            {'board': other_board.id, 'title': 'Neu'},
        )
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.board_id, self.board.id)

    def test_patch_returns_400_when_assignee_is_not_board_participant(self):
        self._auth(self.token_yasef)
        response = self._patch(
            self.task.id,
            {'assignee_id': self.outsider.id},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('assignee_id', response.data)

    def test_patch_partial_update_keeps_other_fields_unchanged(self):
        self._auth(self.token_yasef)
        response = self._patch(self.task.id, {'title': 'Neu'})
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Neu')
        self.assertEqual(self.task.priority, 'medium')

class TaskDeleteTests(APITestCase):
    def setUp(self):
        self.yasef = User.objects.create_user(
            email='yasef@example.com',
            fullname='Yasef',
            password='geheim123',
        )
        self.creator = User.objects.create_user(
            email='creator@example.com',
            fullname='Creator',
            password='geheim123',
        )
        self.another_member = User.objects.create_user(
            email='another@example.com',
            fullname='Another',
            password='geheim123',
        )
        self.outsider = User.objects.create_user(
            email='outsider@example.com',
            fullname='Outsider',
            password='geheim123',
        )
        self.token_yasef = Token.objects.create(user=self.yasef)
        self.token_creator = Token.objects.create(user=self.creator)
        self.token_another = Token.objects.create(user=self.another_member)
        self.token_outsider = Token.objects.create(user=self.outsider)
        self.board = Board.objects.create(title='Board', owner=self.yasef)
        self.board.members.add(self.creator, self.another_member)
        self.task = Task.objects.create(
            board=self.board,
            creator=self.creator,
            title='Task',
            status='to-do',
            priority='medium',
        )

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def _delete(self, task_id):
        return self.client.delete(f'/api/tasks/{task_id}/')

    def test_delete_returns_401_when_no_token(self):
        response = self._delete(self.task.id)
        self.assertEqual(response.status_code, 401)

    def test_delete_returns_404_when_task_does_not_exist(self):
        self._auth(self.token_yasef)
        response = self._delete(999999)
        self.assertEqual(response.status_code, 404)

    def test_delete_returns_403_when_user_is_stranger(self):
        self._auth(self.token_outsider)
        response = self._delete(self.task.id)
        self.assertEqual(response.status_code, 403)

    def test_delete_returns_403_when_user_is_member_but_not_creator(self):
        self._auth(self.token_another)
        response = self._delete(self.task.id)
        self.assertEqual(response.status_code, 403)

    def test_delete_returns_204_when_user_is_creator(self):
        self._auth(self.token_creator)
        response = self._delete(self.task.id)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(pk=self.task.id).exists())

    def test_delete_returns_204_when_user_is_board_owner(self):
        self._auth(self.token_yasef)
        response = self._delete(self.task.id)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(pk=self.task.id).exists())

class AssignedTasksTests(APITestCase):
    def setUp(self):
        self.yasef = User.objects.create_user(
            email='yasef@example.com',
            fullname='Yasef',
            password='geheim123',
        )
        self.other = User.objects.create_user(
            email='other@example.com',
            fullname='Other',
            password='geheim123',
        )
        self.token_yasef = Token.objects.create(user=self.yasef)
        self.token_other = Token.objects.create(user=self.other)
        self.board = Board.objects.create(title='Board', owner=self.yasef)
        self.task_assigned = Task.objects.create(
            board=self.board,
            creator=self.yasef,
            assignee=self.yasef,
            title='Assigned to Yasef',
            status='to-do',
            priority='medium',
        )
        self.task_reviewing = Task.objects.create(
            board=self.board,
            creator=self.yasef,
            reviewer=self.yasef,
            title='Reviewing Yasef',
            status='to-do',
            priority='medium',
        )
        self.task_neither = Task.objects.create(
            board=self.board,
            creator=self.yasef,
            title='Just creator',
            status='to-do',
            priority='medium',
        )

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_returns_401_when_no_token(self):
        response = self.client.get('/api/tasks/assigned-to-me/')
        self.assertEqual(response.status_code, 401)

    def test_returns_only_tasks_where_user_is_assignee(self):
        self._auth(self.token_yasef)
        response = self.client.get('/api/tasks/assigned-to-me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.task_assigned.id)

    def test_returns_empty_list_when_user_has_no_assigned_tasks(self):
        self._auth(self.token_other)
        response = self.client.get('/api/tasks/assigned-to-me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_response_contains_board_as_integer(self):
        self._auth(self.token_yasef)
        response = self.client.get('/api/tasks/assigned-to-me/')
        self.assertEqual(response.data[0]['board'], self.board.id)

class ReviewingTasksTests(APITestCase):
    def setUp(self):
        self.yasef = User.objects.create_user(
            email='yasef@example.com',
            fullname='Yasef',
            password='geheim123',
        )
        self.other = User.objects.create_user(
            email='other@example.com',
            fullname='Other',
            password='geheim123',
        )
        self.token_yasef = Token.objects.create(user=self.yasef)
        self.token_other = Token.objects.create(user=self.other)
        self.board = Board.objects.create(title='Board', owner=self.yasef)
        self.task_assigned = Task.objects.create(
            board=self.board,
            creator=self.yasef,
            assignee=self.yasef,
            title='Assigned to Yasef',
            status='to-do',
            priority='medium',
        )
        self.task_reviewing = Task.objects.create(
            board=self.board,
            creator=self.yasef,
            reviewer=self.yasef,
            title='Reviewing Yasef',
            status='to-do',
            priority='medium',
        )
        self.task_neither = Task.objects.create(
            board=self.board,
            creator=self.yasef,
            title='Just creator',
            status='to-do',
            priority='medium',
        )

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_returns_401_when_no_token(self):
        response = self.client.get('/api/tasks/reviewing/')
        self.assertEqual(response.status_code, 401)

    def test_returns_only_tasks_where_user_is_reviewer(self):
        self._auth(self.token_yasef)
        response = self.client.get('/api/tasks/reviewing/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.task_reviewing.id)

    def test_returns_empty_list_when_user_has_no_reviewing_tasks(self):
        self._auth(self.token_other)
        response = self.client.get('/api/tasks/reviewing/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_response_contains_board_as_integer(self):
        self._auth(self.token_yasef)
        response = self.client.get('/api/tasks/reviewing/')
        self.assertEqual(response.data[0]['board'], self.board.id)

class CommentListTests(APITestCase):
    def setUp(self):
        self.yasef = User.objects.create_user(
            email='yasef@example.com',
            fullname='Yasef Mustermann',
            password='secret123',
        )
        self.member = User.objects.create_user(
            email='member@example.com',
            fullname='Maria Member',
            password='secret123',
        )
        self.stranger = User.objects.create_user(
            email='stranger@example.com',
            fullname='Sam Stranger',
            password='secret123',
        )
        self.board = Board.objects.create(title='Board 1', owner=self.yasef)
        self.board.members.add(self.member)
        self.task = Task.objects.create(
            board=self.board,
            title='Task 1',
            creator=self.yasef,
            status='to-do',
            priority='medium',
        )
        self.comment_old = Comment.objects.create(
            task=self.task,
            author=self.yasef,
            content='First comment',
        )
        self.comment_new = Comment.objects.create(
            task=self.task,
            author=self.member,
            content='Second comment',
        )
        self.url = f'/api/tasks/{self.task.pk}/comments/'

    def _auth(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_returns_401_when_not_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_returns_404_when_task_does_not_exist(self):
        self._auth(self.yasef)
        response = self.client.get('/api/tasks/9999/comments/')
        self.assertEqual(response.status_code, 404)

    def test_returns_403_when_user_is_stranger(self):
        self._auth(self.stranger)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_returns_200_with_correct_fields_when_owner(self):
        self._auth(self.yasef)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        first = response.data[0]
        self.assertEqual(
            set(first.keys()),
            {'id', 'created_at', 'author', 'content'},
        )
        self.assertEqual(first['author'], 'Yasef Mustermann')

    def test_returns_comments_in_chronological_order(self):
        self._auth(self.yasef)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['id'], self.comment_old.pk)
        self.assertEqual(response.data[1]['id'], self.comment_new.pk)

class CommentCreateTests(APITestCase):
    def setUp(self):
        self.yasef = User.objects.create_user(
            email='yasef@example.com',
            fullname='Yasef Mustermann',
            password='secret123',
        )
        self.member = User.objects.create_user(
            email='member@example.com',
            fullname='Maria Member',
            password='secret123',
        )
        self.stranger = User.objects.create_user(
            email='stranger@example.com',
            fullname='Sam Stranger',
            password='secret123',
        )
        self.board = Board.objects.create(title='Board 1', owner=self.yasef)
        self.board.members.add(self.member)
        self.task = Task.objects.create(
            board=self.board,
            title='Task 1',
            creator=self.yasef,
            status='to-do',
            priority='medium',
        )
        self.url = f'/api/tasks/{self.task.pk}/comments/'

    def _auth(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def _payload(self, **overrides):
        data = {'content': 'A new comment'}
        data.update(overrides)
        return data

    def test_returns_401_when_not_authenticated(self):
        response = self.client.post(self.url, self._payload(), format='json')
        self.assertEqual(response.status_code, 401)

    def test_returns_404_when_task_does_not_exist(self):
        self._auth(self.yasef)
        response = self.client.post(
            '/api/tasks/9999/comments/',
            self._payload(),
            format='json',
        )
        self.assertEqual(response.status_code, 404)

    def test_returns_403_when_user_is_stranger(self):
        self._auth(self.stranger)
        response = self.client.post(self.url, self._payload(), format='json')
        self.assertEqual(response.status_code, 403)

    def test_returns_400_when_content_is_empty(self):
        self._auth(self.yasef)
        response = self.client.post(
            self.url,
            self._payload(content=''),
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_returns_201_and_persists_comment_when_owner(self):
        self._auth(self.yasef)
        response = self.client.post(self.url, self._payload(), format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.author, self.yasef)
        self.assertEqual(comment.task, self.task)
        self.assertEqual(comment.content, 'A new comment')

    def test_response_contains_correct_fields(self):
        self._auth(self.yasef)
        response = self.client.post(self.url, self._payload(), format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            set(response.data.keys()),
            {'id', 'created_at', 'author', 'content'},
        )
        self.assertEqual(response.data['author'], 'Yasef Mustermann')

class CommentDeleteTests(APITestCase):
    def setUp(self):
        self.yasef = User.objects.create_user(
            email='yasef@example.com',
            fullname='Yasef Mustermann',
            password='secret123',
        )
        self.member = User.objects.create_user(
            email='member@example.com',
            fullname='Maria Member',
            password='secret123',
        )
        self.stranger = User.objects.create_user(
            email='stranger@example.com',
            fullname='Sam Stranger',
            password='secret123',
        )
        self.board = Board.objects.create(title='Board 1', owner=self.yasef)
        self.board.members.add(self.member)
        self.task_a = Task.objects.create(
            board=self.board,
            title='Task A',
            creator=self.yasef,
            status='to-do',
            priority='medium',
        )
        self.task_b = Task.objects.create(
            board=self.board,
            title='Task B',
            creator=self.yasef,
            status='to-do',
            priority='medium',
        )
        self.comment = Comment.objects.create(
            task=self.task_a,
            author=self.member,
            content='Member comment on Task A',
        )
        self.url = f'/api/tasks/{self.task_a.pk}/comments/{self.comment.pk}/'

    def _auth(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_returns_401_when_not_authenticated(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)

    def test_returns_404_when_task_does_not_exist(self):
        self._auth(self.member)
        url = f'/api/tasks/9999/comments/{self.comment.pk}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_returns_404_when_comment_does_not_exist(self):
        self._auth(self.member)
        url = f'/api/tasks/{self.task_a.pk}/comments/9999/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_returns_404_when_comment_does_not_belong_to_url_task(self):
        self._auth(self.member)
        url = f'/api/tasks/{self.task_b.pk}/comments/{self.comment.pk}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_returns_403_when_user_is_not_author(self):
        self._auth(self.yasef)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)

    def test_returns_204_when_user_is_author(self):
        self._auth(self.member)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Comment.objects.count(), 0)