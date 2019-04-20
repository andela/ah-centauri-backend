from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an article to edit its details.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.author == request.user

class IsVerified(permissions.BasePermission):
    """
    Custom permission to only allow verified users
    to get a list of authors and their profiles. 
    """
    message = ("The email linked to your account has not been verified."
               " Please verify your account using the email verification link "
               "if you would like to enjoy all our features.")
               
    def has_permission(self, request, view):
        # REad authors permissions are only allowed to authenticated and verified users
        return request.user.is_verified
