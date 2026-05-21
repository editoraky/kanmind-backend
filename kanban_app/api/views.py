from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from kanban_app.models import Board, Task
from kanban_app.api.serializers import (
    BoardSerializer,
    BoardDetailSerializer,
    BoardUpdateSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskListSerializer,
)
from kanban_app.api.permissions import (
    IsBoardOwnerOrMember,
    IsBoardOwner,
    CanCreateTaskOnBoard,
    IsTaskBoardMember,
    IsTaskCreatorOrBoardOwner,
)


class BoardListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BoardSerializer

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BoardDetailView(RetrieveUpdateDestroyAPIView):
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    queryset = Board.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardOwnerOrMember()]


class TaskCreateView(CreateAPIView):
    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated, CanCreateTaskOnBoard]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class TaskDetailView(RetrieveUpdateDestroyAPIView):
    http_method_names = ['patch', 'delete', 'head', 'options']
    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsTaskBoardMember()]

class AssignedTasksView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskListSerializer

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)

class ReviewingTasksView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskListSerializer

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)
