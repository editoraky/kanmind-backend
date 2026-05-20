from rest_framework.permissions import BasePermission


class IsBoardOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.owner == user or obj.members.filter(pk=user.pk).exists()


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

