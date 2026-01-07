from django.urls import path
from .views import (
    TodoListCreateAPIView,
    TodoDetailAPIView,
    CreateTenantAPIView,
    CurrentTenantAPIView,
    UserProfileUpdateAPIView,
    TenantMembersAPIView,
    UserProfileAPIView
)




urlpatterns = [
    path('todos/',TodoListCreateAPIView.as_view()),
    path('todos/<int:pk>/',TodoDetailAPIView.as_view()),
    path('create-tenant/', CreateTenantAPIView.as_view()),
    path('current-tenant/', CurrentTenantAPIView.as_view()),  
    path('members/', TenantMembersAPIView.as_view()),
    path('members/<int:user_id>/role/', UserProfileUpdateAPIView.as_view()),
    path('auth/me/', UserProfileAPIView.as_view(), name='user_profile'),
]