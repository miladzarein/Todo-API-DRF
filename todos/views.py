from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Todo
from .serializers import TodoSerializer



class TodoListCreateAPIView(APIView):
    """List all todos or create a new one."""


    def get(self,request):
        todos = Todo.objects.all()
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data)
    

    def post(self, request):
        serializer = TodoSerializer(data=serializer.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class TodoDetailAPIView(APIView):
    """
    Handle retrieving, updating, or deleting a single Todo object.
    """
    def get_object(self,pk):
        try:
            return Todo.objects.get(pk=pk)
        except Todo.DoesNotExist:
            return None
        
    def get(self,request,pk):
        todo = self.get_object(pk)
        if not todo:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TodoSerializer(todo)
        return Response (serializer.data)