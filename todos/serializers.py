from rest_framework import serializers
from .models import Todo




class TodoSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username',read_only=True)

    class Meta:
        model = Todo
        fields = ['id','title','completed','created_at','owner_username']
        read_only_fields = ['id', 'created_at','owner_username']