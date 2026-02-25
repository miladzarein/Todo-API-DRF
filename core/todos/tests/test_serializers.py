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