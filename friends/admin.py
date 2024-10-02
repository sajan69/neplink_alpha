from django.contrib import admin
from .models import FriendRequest, Friendship

# Register your models here.

admin.site.register(FriendRequest)
admin.site.register(Friendship)