import pytest
from django.contrib.auth.models import User
from todos.models import Todo
from todos.serializers import TodoSerializer, UserSerializer


@pytest.mark.django_db
class TestUserSerializer:
    """Tests for UserSerializer"""
    
    def test_user_serializer_validation(self):
        """Test UserSerializer validation and creation"""
        # Test data
        data = {
            'username': 'serializeruser',
            'password': 'testpass123',
            'email': 'serializer@example.com'
        }
        
        # Test validation
        serializer = UserSerializer(data=data)
        assert serializer.is_valid() is True
        
        # Test creating user
        user = serializer.save()
        assert user.username == 'serializeruser'
        assert user.email == 'serializer@example.com'
        assert user.check_password('testpass123') is True

    def test_user_serializer_password_write_only(self):
        """Test password field is write-only"""
        user = User.objects.create_user(
            username='testuser',
            password='hidden'
        )
        
        serializer = UserSerializer(user)
        data = serializer.data
        
        # Password should not be in output
        assert 'password' not in data
        assert 'username' in data
        assert 'email' in data

@pytest.mark.django_db
class TestTodoSerializer:
    """Tests for TodoSerializer"""
    
    def test_todo_serializer_output(self):
        """Test TodoSerializer serialization"""
        # Setup
        user = User.objects.create_user(username='serializerowner')
        tenant = user.userprofile.tenant
        
        todo = Todo.objects.create(
            title='Serializer Test Todo',
            owner=user,
            tenant=tenant
        )
        
        # Test serialization
        serializer = TodoSerializer(todo)
        data = serializer.data
        
        assert data['title'] == 'Serializer Test Todo'
        assert data['owner_username'] == 'serializerowner'
        assert data['tenant_name'] == tenant.name
        assert data['completed'] is False
        assert 'created_at' in data

    def test_todo_serializer_validation(self):
        """Test TodoSerializer validation"""
        # Valid data
        valid_data = {'title': 'Valid Todo'}
        serializer = TodoSerializer(data=valid_data)
        assert serializer.is_valid() is True
        
        # Invalid data - empty title
        invalid_data = {'title': ''}
        serializer = TodoSerializer(data=invalid_data)
        assert serializer.is_valid() is False
        assert 'title' in serializer.errors