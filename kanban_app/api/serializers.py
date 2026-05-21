from rest_framework import serializers
from django.contrib.auth import get_user_model

from kanban_app.models import Board, Task
from auth_app.api.serializers import UserSerializer

User = get_user_model()


class BoardSerializer(serializers.ModelSerializer):
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
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
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
        return obj.comments.count()


class BoardDetailSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'members',
            'tasks',
        ]

class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'members',
            'owner_data',
            'members_data',
        ]

class TaskCreateSerializer(serializers.ModelSerializer):
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
        return obj.comments.count()

    def validate(self, attrs):
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
        return user == board.owner or board.members.filter(pk=user.pk).exists()


class TaskUpdateSerializer(serializers.ModelSerializer):
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
        return user == board.owner or board.members.filter(pk=user.pk).exists()