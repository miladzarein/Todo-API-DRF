from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Todo,UserProfile
from .serializers import TodoSerializer,UserProfileSerializer,UserSerializer
from .permissions import IsTenantMember, IsTodoOwner,IsOwnerOrAdmin,IsOwnerOnly
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.cache import cache
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle


class TodoListCreateAPIView(APIView):
    """List all todos or create a new one."""
    permission_classes = [IsTenantMember]
    
    throttle_classes = [UserRateThrottle, ScopedRateThrottle]
    throttle_scope = 'todos'
    @swagger_auto_schema(responses={200: TodoSerializer(many=True)})
    def get(self,request):
        tenant = request.user.userprofile.tenant
        cache_key = f"todos_tenant_{tenant.id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        todos = Todo.objects.filter(tenant=tenant)
        serializer = TodoSerializer(todos, many=True)

        cache.set(cache_key, serializer.data, timeout=60)
        return Response(serializer.data)
    
    @swagger_auto_schema(request_body=TodoSerializer)
    def post(self, request):
        tenant = request.user.userprofile.tenant
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user,tenant=tenant)
            
            cache_key = f"todos_tenant_{tenant.id}"
            cache.delete(cache_key)
            
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class TodoDetailAPIView(APIView):
    permission_classes = [IsTenantMember, IsTodoOwner]
    """
    Handle retrieving, updating, or deleting a single Todo object.
    """
    throttle_classes = [UserRateThrottle, ScopedRateThrottle]
    throttle_scope = 'todos'
    @swagger_auto_schema(responses={200: TodoSerializer(many=True)})
    def get_object(self,pk):
        try:
            tenant = self.request.user.userprofile.tenant
            return Todo.objects.get(pk=pk,tenant=tenant)
        except Todo.DoesNotExist:
            return None
    @swagger_auto_schema(responses={200: TodoSerializer(many=True)})    
    def get(self,request,pk):
        tenant = request.user.userprofile.tenant
        cache_key = f"todo_{tenant.id}_{pk}"

        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        
        todo = self.get_object(pk)
        if not todo:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND
                )
        self.check_object_permissions(request, todo)
        serializer = TodoSerializer(todo)
        cache.set(cache_key, serializer.data, timeout=120)
        return Response (serializer.data)
    

    @swagger_auto_schema(request_body=TodoSerializer)
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

            tenant_id = request.user.userprofile.tenant.id
            cache.delete(f"todo_{tenant_id}_{pk}")
            cache.delete(f"todos_tenant_{tenant_id}")

            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(request_body=TodoSerializer)
    def delete(self,request,pk):
        todo = self.get_object(pk)
        if not todo:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(request, todo)
        todo.delete()

        tenant_id = request.user.userprofile.tenant.id
        cache.delete(f"todo_{tenant_id}_{pk}")
        cache.delete(f"todos_tenant_{tenant_id}")
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class UserProfileUpdateAPIView(APIView):
    """
    API for updating user role (only for admin/owner)
    """
    permission_classes = [IsOwnerOrAdmin]
    @swagger_auto_schema(request_body=TodoSerializer)
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
    @swagger_auto_schema(responses={200: TodoSerializer(many=True)})
    def get(self, request):
        tenant = request.user.userprofile.tenant
        cache_key = f"tenant_members_{tenant.id}"

        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        members = UserProfile.objects.filter(tenant=tenant)
        serializer = UserProfileSerializer(members, many=True)
        cache.set(cache_key, serializer.data, 300)
        
        return Response(serializer.data)
    

class CurrentTenantAPIView(APIView):
    """
    API to get current tenant data
    """
    
    permission_classes = [IsTenantMember]
    
    throttle_classes = [AnonRateThrottle, ScopedRateThrottle]
    throttle_scope = 'register'
    @swagger_auto_schema(responses={200: TodoSerializer(many=True)})
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
    
    throttle_classes = [AnonRateThrottle, ScopedRateThrottle]
    throttle_scope = 'register'
    @swagger_auto_schema(request_body=TodoSerializer)
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


class UserProfileAPIView(APIView):
    """
    API endpoint to retrieve the current user's profile.
    Returns full profile if exists, otherwise basic user info.
    """
    permission_classes = [IsTenantMember]
    @swagger_auto_schema(responses={200: TodoSerializer(many=True)})
    def get(self, request):
        user = request.user
        try:
            user_profile = user.userprofile
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data)
        except:
            return Response({
                'username': user.username,
                'email': user.email,
                'error': 'User profile not found'
            }, status=400)