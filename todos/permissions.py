from rest_framework import permissions



class IsTenantMember(permissions.BasePermission):
    """
    Permission to check if user belongs to the tenant
    """
    def has_permission(self, request, view):
        #just to write it myself. it's equal to IsAuthenticated
        return request.user.is_authenticated


class IsTodoOwner(permissions.BasePermission):
    """
    Permission to check if user owns the todo item
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user and obj.tenant == request.user.userprofile.tenant
    
class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is owner or admin
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.userprofile.role in ['owner', 'admin']
    
class IsOwnerOnly(permissions.BasePermission):
    """
    Permission to check if user is owner only
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.userprofile.role == 'owner'