from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound

from kanban_app.models import Board, Task


class IsBoardOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.owner == user or obj.members.filter(pk=user.pk).exists()


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class CanCreateTaskOnBoard(BasePermission):
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        board_id = request.data.get('board')
        if board_id is None:
            return True
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise NotFound('Board not found.')
        user = request.user
        return user == board.owner or board.members.filter(pk=user.pk).exists()

class IsTaskBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.board
        return board.owner == user or board.members.filter(pk=user.pk).exists()


class IsTaskCreatorOrBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.creator == user or obj.board.owner == user

class CanAccessTaskComments(BasePermission):
    def has_permission(self, request, view):
        task_pk = view.kwargs.get('task_pk')
        if task_pk is None:
            return True
        try:
            task = Task.objects.get(pk=task_pk)
        except Task.DoesNotExist:
            raise NotFound('Task not found.')
        user = request.user
        board = task.board
        return user == board.owner or board.members.filter(pk=user.pk).exists()


class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user