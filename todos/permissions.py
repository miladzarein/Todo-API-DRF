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
    
