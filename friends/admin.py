from django.contrib import admin
from .models import FriendRequest, Friendship

# Register your models here.

admin.site.register(FriendRequest)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'created_at', 'friend_online_status')  # Show the friend online status
    list_filter = ('created_at',)  # Filter by created date
    search_fields = ('user__username', 'friend__username')  # Search functionality

    def friend_online_status(self, obj):
        """Method to get the friend's online status."""
        return obj.friend.is_online()  # Use the is_online method from User model
    friend_online_status.short_description = 'Friend Online Status'  # Custom header for the column


admin.site.register(Friendship, FriendshipAdmin)  # Register the Friendship admin
