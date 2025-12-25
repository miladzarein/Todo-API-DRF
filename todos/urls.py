from django.urls import path
from .views import TodoListCreateAPIView,TodoDetailAPIView




urlpatterns = [
    path('todos/',TodoListCreateAPIView.as_view()),
    path('todos/<int:pk>/',TodoDetailAPIView.as_view())
]