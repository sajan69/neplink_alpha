
from django.contrib import admin
from .models import User
from friends.models import Friendship

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'last_logged_in', 'is_online_display', 'first_name', 'last_name')  # Include last_logged_in and online status
    list_filter = ('last_logged_in',)  # Filter by last logged-in time
    search_fields = ('username', 'email', 'first_name', 'last_name')  # Search fields

    def is_online_display(self, obj):
        """Display whether the user is online based on last_logged_in."""
        return obj.is_online()  # Use the is_online method from User model
    is_online_display.short_description = 'Online Status'  # Custom header for the column

admin.site.register(User, UserAdmin)  # Register the new User admin
