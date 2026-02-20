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