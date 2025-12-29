from django.db import models
from django.contrib.auth.models import User



class Tenant(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name='owned_tenants')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant,on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[('owner', 'Owner'), ('admin', 'Admin'), ('member', 'Member')],
        default='member'
    )
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
class Todo(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='todos')
    owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name='todos')
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title