from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound

from kanban_app.models import Board


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