from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile, Tenant


@receiver(post_save,sender=User)
def create_user_profile(sender,instance,created,**kwargs):
    if not created:
        return
    
    try:
        instance.userprofile
        return
    except ObjectDoesNotExist:
        pass


    tenant = Tenant.objects.create(
        name =f'Personal-Tenant - {instance.username}',
        owner = instance
    )



    UserProfile.objects.create(
        user = instance,
        tenant = tenant,
        role = 'owner'
    )