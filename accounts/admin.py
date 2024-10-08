
from django.contrib import admin

from django import forms

from accounts.services import NotificationService
from .models import Notification, User
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


class NotificationAdminForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")

        # Ensure the user is specified
        if not user:
            raise forms.ValidationError("You must specify a user.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Get cleaned data fields
        user = self.cleaned_data.get("user")
        title = self.cleaned_data.get("title")
        body = self.cleaned_data.get("body")
        link = self.cleaned_data.get("link")

        # Notify the user
        userids = [user.id]
        NotificationService.send_notification_to_userids_admin(title, body, userids, link)
        
        # Save the instance only once
        if commit:
            instance.save()

        return instance


class NotificationAdmin(admin.ModelAdmin):
    form = NotificationAdminForm
    list_display = ('title', 'user', 'timestamp', 'read', 'link')  # Include the link field

    # 

admin.site.register(Notification, NotificationAdmin)

