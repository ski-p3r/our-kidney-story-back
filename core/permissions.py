from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners or admins to access an object.
    """
    def has_object_permission(self, request, view, obj):
        # Allow if user is admin
        if request.user.role == 'ADMIN':
            return True
            
        # Check if the object has a user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        # Check if the object has an author attribute
        if hasattr(obj, 'author'):
            return obj.author == request.user
            
        return False
