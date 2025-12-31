from rest_framework import permissions



class IsTenantMember(permissions.BasePermission):
    """
    Permission to check if user belongs to the tenant
    """
    def has_permission(self, request, view):
        #just to write it myself. it's equal to IsAuthenticated
        return request.user.is_authenticated

