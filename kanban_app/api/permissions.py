"""Object- and request-level permissions for the Kanban API."""

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound

from kanban_app.models import Board, Task


class IsBoardOwnerOrMember(BasePermission):
    """Allow access when the user owns the board or is one of its members."""

    def has_object_permission(self, request, view, obj):
        """Grant access if the request user is the board's owner or a member."""
        user = request.user
        return obj.owner == user or obj.members.filter(pk=user.pk).exists()


class IsBoardOwner(BasePermission):
    """Restrict access to the board's owner."""

    def has_object_permission(self, request, view, obj):
        """Grant access only when the request user owns the board."""
        return obj.owner == request.user


class CanCreateTaskOnBoard(BasePermission):
    """Allow task creation only on boards the user participates in.

    Resolves the ``board`` id from the POST payload and rejects unknown
    boards with a 404 instead of leaking permission information.
    """

    def has_permission(self, request, view):
        """Check board membership for POST requests; pass through other methods."""
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
    """Allow task access when the user is owner or member of the task's board."""

    def has_object_permission(self, request, view, obj):
        """Grant access if the user participates in the task's parent board."""
        user = request.user
        board = obj.board
        return board.owner == user or board.members.filter(pk=user.pk).exists()


class IsTaskCreatorOrBoardOwner(BasePermission):
    """Restrict destructive task actions to its creator or the board's owner."""

    def has_object_permission(self, request, view, obj):
        """Grant access when the user created the task or owns its board."""
        user = request.user
        return obj.creator == user or obj.board.owner == user

class CanAccessTaskComments(BasePermission):
    """Allow comment access when the user participates in the task's board.

    Looks up the task by its URL kwarg and returns 404 when it does not
    exist so callers cannot probe for hidden task IDs.
    """

    def has_permission(self, request, view):
        """Resolve the task from the URL and check board participation."""
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
    """Restrict comment deletion to the author who wrote it."""

    def has_object_permission(self, request, view, obj):
        """Grant access only when the request user is the comment's author."""
        return obj.author == request.user