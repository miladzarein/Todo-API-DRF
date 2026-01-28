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

@pytest.mark.django_db
def test_user_str():
    """Test user string representation"""
    user = User.objects.create_user(username="user1")
    assert str(user) == "user1"

@pytest.mark.django_db
def test_create_todo():
    """Test creating a todo"""
    # Create user (signals will create profile and tenant)
    user = User.objects.create_user(
        username="todoowner",
        password="pass123",
    )

    # Get tenant created by signal
    tenant = user.userprofile.tenant

    todo = Todo.objects.create(
        title="Test Todo",
        owner=user,
        tenant=tenant,
    )

    assert todo.title == "Test Todo"
    assert todo.owner == user
    assert todo.tenant == tenant
    assert todo.completed is False


@pytest.mark.django_db
def test_todo_str():
    """Test todo string representation"""
    user = User.objects.create_user(username="user2")
    tenant = user.userprofile.tenant

    todo = Todo.objects.create(
        title="My Todo",
        owner=user,
        tenant=tenant,
    )

    assert str(todo) == "My Todo"