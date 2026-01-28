import pytest
from django.contrib.auth.models import User
from todos.models import Todo


@pytest.mark.django_db
def test_create_user():
    """Test user creation"""
    user = User.objects.create_user(
        username="testuser",
        password="testpass123",
        email="test@example.com",
    )

    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.check_password("testpass123") is True