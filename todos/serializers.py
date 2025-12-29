from rest_framework import serializers
from .models import Todo,Tenant,UserProfile
from django.contrib.auth.models import User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','password']
        extra_kwargs = {'password':{'write_only':True}}



class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'tenant', 'role']
        read_only_fields = ['id', 'username', 'email', 'tenant']


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id','name','owner','created_at']
        read_only_fields = ['id','owner','created_at']


class TodoSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username',read_only=True)
    tenant_name = serializers.CharField(source='tenant.name',read_only=True)

    class Meta:
        model = Todo
        fields = ['id','title','completed','created_at','owner_username','tenant_name']
        read_only_fields = ['id', 'created_at','owner_username','tenant_name']