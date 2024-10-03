from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    contact = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return self.username
 