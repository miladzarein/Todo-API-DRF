import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from todos.permissions import IsTenantMember
from todos.models import Todo


@pytest.mark.django_db
def test_is_tenant_member_authenticated():
    """Authenticated users should have permission"""
    factory = RequestFactory()
    user = User.objects.create_user(username="user1", password="pass123")

    permission = IsTenantMember()
    request = factory.get("/")
    request.user = user

    assert request.user.is_authenticated is True
    assert permission.has_permission(request, None) is True



@pytest.mark.django_db
def test_is_tenant_member_anonymous():
    """Anonymous users should NOT have permission"""
    factory = RequestFactory()

    permission = IsTenantMember()
    request = factory.get("/")
    request.user = AnonymousUser()

    assert request.user.is_authenticated is False
    assert permission.has_permission(request, None) is False


@pytest.mark.django_db
def test_todo_ownership():
    """Each todo should belong to its correct owner"""
    owner = User.objects.create_user(username="owner", password="pass123")
    other_user = User.objects.create_user(username="other", password="pass123")

    owner_tenant = owner.userprofile.tenant
    other_tenant = other_user.userprofile.tenant

    owner_todo = Todo.objects.create(
        title="Owner's Todo",
        owner=owner,
        tenant=owner_tenant,
    )

    other_todo = Todo.objects.create(
        title="Other's Todo",
        owner=other_user,
        tenant=other_tenant,
    )

    assert owner_todo.owner == owner
    assert other_todo.owner == other_user
    assert owner_todo.owner != other_todo.owner


@pytest.mark.django_db
def test_todo_tenant_separation():
    """Todos should be separated by tenant"""
    owner = User.objects.create_user(username="owner2", password="pass123")
    other_user = User.objects.create_user(username="other2", password="pass123")

    owner_tenant = owner.userprofile.tenant
    other_tenant = other_user.userprofile.tenant

    owner_todo = Todo.objects.create(
        title="Owner Todo",
        owner=owner,
        tenant=owner_tenant,
    )

    other_todo = Todo.objects.create(
        title="Other Todo",
        owner=other_user,
        tenant=other_tenant,
    )

    assert owner_todo.tenant != other_todo.tenant


@pytest.mark.django_db
def test_password_hashing():
    """Passwords should be hashed and verifiable"""
    user = User.objects.create_user(
        username="securityuser",
        password="plaintextpassword",
    )

    assert user.password != "plaintextpassword"
    assert user.check_password("plaintextpassword") is True
    assert user.check_password("wrongpassword") is False




@pytest.mark.django_db
def test_default_user_permissions():
    """Regular users should not be staff or superuser by default"""
    user = User.objects.create_user(username="regularuser")

    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.is_active is True