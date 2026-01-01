from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Todo,UserProfile
from .serializers import TodoSerializer,UserProfileSerializer,UserSerializer
from .permissions import IsTenantMember, IsTodoOwner,IsOwnerOrAdmin,IsOwnerOnly
from django.shortcuts import get_object_or_404

class TodoListCreateAPIView(APIView):
    """List all todos or create a new one."""
    permission_classes = [IsTenantMember]

    def get(self,request):
        tenant = request.user.userprofile.tenant
        todos = Todo.objects.filter(tenant=tenant)
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data)
    

    def post(self, request):
        tenant = request.user.userprofile.tenant
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user,tenant=tenant)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class TodoDetailAPIView(APIView):
    permission_classes = [IsTenantMember, IsTodoOwner]
    """
    Handle retrieving, updating, or deleting a single Todo object.
    """
    def get_object(self,pk):
        try:
            tenant = self.request.user.userprofile.tenant
            return Todo.objects.get(pk=pk,tenant=tenant)
        except Todo.DoesNotExist:
            return None
        
    def get(self,request,pk):
        todo = self.get_object(pk)
        if not todo:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND
                )
        self.check_object_permissions(request, todo)
        serializer = TodoSerializer(todo)
        return Response (serializer.data)
    


    def put(self,request,pk):
        todo = self.get_object(pk)
        if not todo:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, todo)
        serializer = TodoSerializer(todo,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self,request,pk):
        todo = self.get_object(pk)
        if not todo:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, todo)
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class UserProfileUpdateAPIView(APIView):
    """
    API for updating user role (only for admin/owner)
    """
    permission_classes = [IsOwnerOrAdmin]
    
    def put(self, request, user_id):
        user_profile = get_object_or_404(
            UserProfile, 
            user__id=user_id, 
            tenant=request.user.userprofile.tenant
        )
        
        # User cannot change their own role
        if user_profile.user == request.user:
            return Response(
                {"detail": "You cannot change your own role."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Admin cannot modify owner's role
        if request.user.userprofile.role == 'admin' and user_profile.role == 'owner':
            return Response(
                {"detail": "Admin cannot modify owner's role."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserProfileSerializer(
            user_profile, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TenantMembersAPIView(APIView):
    """
    API to get all tenant members (Owner only)
    """
    permission_classes = [IsOwnerOnly]
    def get(self, request):
        tenant = request.user.userprofile.tenant
        members = UserProfile.objects.filter(tenant=tenant)
        serializer = UserProfileSerializer(members, many=True)
        return Response(serializer.data)
    

class CurrentTenantAPIView(APIView):
    """
    API to get current tenant data
    """
    permission_classes = [IsTenantMember]
    def get(self, request):
        tenant = request.user.userprofile.tenant
        return Response({
            'tenant_id': tenant.id,
            'tenant_name': tenant.name,
            'owner': tenant.owner.username
        })
    

class CreateTenantAPIView(APIView):
    """
    API for creating a new tenant (registration)
    """
    permission_classes = []  # Public access

    def post(self, request):
        # Create new user
        user_data = {
            'username': request.data.get('username'),
            'password': request.data.get('password'),
            'email': request.data.get('email', '')
        }
        
        user_serializer = UserSerializer(data=user_data)
        if not user_serializer.is_valid():
            return Response(
                user_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = user_serializer.save()
        user.set_password(user_data['password'])
        user.save()

        # Update tenant name
        tenant = user.userprofile.tenant
        tenant_name = request.data.get('tenant_name', f"Tenant-{user.username}")
        tenant.name = tenant_name
        tenant.save()

        return Response({
            'message': 'Tenant created successfully',
            'user_id': user.id,
            'tenant_id': tenant.id,
            'tenant_name': tenant.name
        }, status=status.HTTP_201_CREATED)