from rest_framework import serializers
from .models import Todo,Tenant,UserProfile



class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id','name','owner','created_at']
        read_only_fields = ['id','owner','created_at']


class TodoSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username',read_only=True)

    class Meta:
        model = Todo
        fields = ['id','title','completed','created_at','owner_username']
        read_only_fields = ['id', 'created_at','owner_username']