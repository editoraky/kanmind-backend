"""API views for boards, tasks and comments in the Kanban app."""

from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from kanban_app.models import Board, Task, Comment
from kanban_app.api.serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardUpdateSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskListSerializer,
    CommentSerializer,
)
from kanban_app.api.permissions import (
    IsBoardOwnerOrMember,
    IsBoardOwner,
    CanCreateTaskOnBoard,
    IsTaskBoardMember,
    IsTaskCreatorOrBoardOwner,
    CanAccessTaskComments,
    IsCommentAuthor,
)


class BoardListCreateView(ListCreateAPIView):
    """List the boards the current user can access and create new ones."""

    permission_classes = [IsAuthenticated]
    serializer_class = BoardSerializer

    def get_queryset(self):
        """Return boards where the user is either the owner or a member."""
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        """Persist the new board with the requesting user as its owner."""
        serializer.save(owner=self.request.user)


class BoardDetailView(RetrieveUpdateDestroyAPIView):
    """Retrieve, partially update or delete a single board."""

    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    queryset = Board.objects.all()

    def get_serializer_class(self):
        """Use the update serializer for PATCH; the detail one otherwise."""
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_permissions(self):
        """Restrict deletes to the owner; reads and updates to owner or members."""
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardOwnerOrMember()]


class TaskCreateView(CreateAPIView):
    """Create a new task on a board the requesting user participates in."""

    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated, CanCreateTaskOnBoard]

    def perform_create(self, serializer):
        """Persist the task with the requesting user recorded as creator."""
        serializer.save(creator=self.request.user)

class TaskDetailView(RetrieveUpdateDestroyAPIView):
    """Partially update or delete a single task."""

    http_method_names = ['patch', 'delete', 'head', 'options']
    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer

    def get_permissions(self):
        """Restrict deletes to creator or board owner; updates to board members."""
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsTaskBoardMember()]

class AssignedTasksView(ListAPIView):
    """List tasks the current user is assigned to."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskListSerializer

    def get_queryset(self):
        """Return tasks whose assignee is the requesting user."""
        return Task.objects.filter(assignee=self.request.user)

class ReviewingTasksView(ListAPIView):
    """List tasks the current user is set as reviewer on."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskListSerializer

    def get_queryset(self):
        """Return tasks whose reviewer is the requesting user."""
        return Task.objects.filter(reviewer=self.request.user)

class CommentListCreateView(ListCreateAPIView):
    """List and create comments for a given task."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, CanAccessTaskComments]

    def get_queryset(self):
        """Return only the comments attached to the task from the URL."""
        return Comment.objects.filter(task_id=self.kwargs['task_pk'])

    def perform_create(self, serializer):
        """Persist the comment, attaching it to the task and current user."""
        serializer.save(
            author=self.request.user,
            task_id=self.kwargs['task_pk'],
        )


class CommentDeleteView(DestroyAPIView):
    """Delete a single comment, restricted to its author."""

    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_queryset(self):
        """Scope the lookup to comments of the task referenced in the URL."""
        return Comment.objects.filter(task_id=self.kwargs['task_pk'])