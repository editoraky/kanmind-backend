"""Serializers for the boards, tasks and comments API."""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from kanban_app.models import Board, Task, Comment
from auth_app.api.serializers import UserSerializer

User = get_user_model()


class BoardSerializer(serializers.ModelSerializer):
    """Compact board representation used by the list and create endpoints.

    Exposes aggregate counters (members, tickets, to-do and high-priority
    tasks) so the frontend can render board cards without extra queries.
    """

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        """Map the serializer fields to the ``Board`` model."""

        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id',
            'members',
        ]

    def get_member_count(self, obj):
        """Return how many users are members of the board."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the total number of tasks on the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the number of tasks currently in the ``to-do`` status."""
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        """Return the number of tasks with ``high`` priority."""
        return obj.tasks.filter(priority='high').count()


class TaskSerializer(serializers.ModelSerializer):
    """Read-oriented task representation with nested user data."""

    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        """Map the serializer fields to the ``Task`` model."""

        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count',
        ]

    def get_comments_count(self, obj):
        """Return the number of comments attached to the task."""
        return obj.comments.count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """Full board payload including nested members and tasks."""

    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        """Expose the board together with its members and tasks."""

        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'members',
            'tasks',
        ]

class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a board's title and member list.

    Accepts ``members`` as a list of user IDs on write and returns the
    expanded ``owner_data`` and ``members_data`` for the response.
    """

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)

    class Meta:
        """Map the update fields to the ``Board`` model."""

        model = Board
        fields = [
            'id',
            'title',
            'members',
            'owner_data',
            'members_data',
        ]

class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a task on a given board.

    Accepts ``assignee_id`` and ``reviewer_id`` on input and validates that
    both users belong to the target board.
    """

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True,
    )
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        """Map the create fields to the ``Task`` model."""

        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee_id',
            'reviewer_id',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count',
        ]

    def get_comments_count(self, obj):
        """Return the number of comments on the newly created task."""
        return obj.comments.count()

    def validate(self, attrs):
        """Reject assignee/reviewer values that are not members of the board."""
        board = attrs.get('board')
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')
        if assignee and not self._is_board_participant(assignee, board):
            raise serializers.ValidationError(
                {'assignee_id': 'Must be a member or owner of the board'}
            )
        if reviewer and not self._is_board_participant(reviewer, board):
            raise serializers.ValidationError(
                {'reviewer_id': 'Must be a member or owner of the board'}
            )
        return attrs

    @staticmethod
    def _is_board_participant(user, board):
        """Return True when the user is the board owner or one of its members."""
        return user == board.owner or board.members.filter(pk=user.pk).exists()


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for partial task updates while keeping the board fixed."""

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False,
        allow_null=True,
    )
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    class Meta:
        """Map the update fields to the ``Task`` model."""

        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'assignee_id',
            'reviewer_id',
            'assignee',
            'reviewer',
            'due_date',
        ]

    def validate(self, attrs):
        """Ensure new assignee/reviewer values are still board participants."""
        board = self.instance.board
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')
        if assignee and not self._is_board_participant(assignee, board):
            raise serializers.ValidationError(
                {'assignee_id': 'Must be a member or owner of the board'}
            )
        if reviewer and not self._is_board_participant(reviewer, board):
            raise serializers.ValidationError(
                {'reviewer_id': 'Must be a member or owner of the board'}
            )
        return attrs

    @staticmethod
    def _is_board_participant(user, board):
        """Return True when the user is the board owner or one of its members."""
        return user == board.owner or board.members.filter(pk=user.pk).exists()

class TaskListSerializer(serializers.ModelSerializer):
    """Read serializer used by the assigned-to-me and reviewing list views."""

    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        """Map the list fields to the ``Task`` model."""

        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count',
        ]

    def get_comments_count(self, obj):
        """Return the number of comments attached to the task."""
        return obj.comments.count()

class CommentSerializer(serializers.ModelSerializer):
    """Serializer for task comments; exposes the author's fullname as a string."""

    author = serializers.CharField(source='author.fullname', read_only=True)

    class Meta:
        """Map the serializer fields to the ``Comment`` model."""

        model = Comment
        fields = ['id', 'created_at', 'author', 'content']