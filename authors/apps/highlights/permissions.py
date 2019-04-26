from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a highlight to edit its details.
    """
    message = ("You are not the owner of this highlight"
               " and cannot access or change it\'s details.")

    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner of the highlight.
        return obj.profile == request.user.profile
