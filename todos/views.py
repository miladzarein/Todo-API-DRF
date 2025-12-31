from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Todo
from .serializers import TodoSerializer
from .permissions import IsTenantMember, IsTodoOwner


class TodoListCreateAPIView(APIView):
    """List all todos or create a new one."""
    permission_classes = [IsTenantMember]

    def get(self,request):
        tenant = request.user.userprofile.tenant
        todos = Todo.objects.filter(tenant=tenant)
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data)
    

    def post(self, request):
        tenant = request.user.userprofile.tenant
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user,tenant=tenant)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class TodoDetailAPIView(APIView):
    """
    Handle retrieving, updating, or deleting a single Todo object.
    """
    def get_object(self,pk,user):
        try:
            return Todo.objects.get(pk=pk,owner=user)
        except Todo.DoesNotExist:
            return None
        
    def get(self,request,pk):
        todo = self.get_object(pk,request.user)
        if not todo:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TodoSerializer(todo)
        return Response (serializer.data)
    


    def put(self,request,pk):
        todo = self.get_object(pk,request.user)
        if not todo:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TodoSerializer(todo,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self,request,pk):
        todo = self.get_object(pk,request.user)
        if not todo:
            return Response(status=status.HTTP_404_NOT_FOUND)
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)