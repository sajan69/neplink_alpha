
from django.contrib import admin

from django import forms

from accounts.services import NotificationService
from .models import Notification, User, OTP
from friends.models import Friendship
from post.models import UserTagSettings
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import ngettext

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'last_logged_in', 'is_online_display', 'first_name', 'last_name', 'is_private', 'show_email', 'show_full_name', 'allow_tagging')  # Include last_logged_in and online status
    list_filter = ('last_logged_in',)  # Filter by last logged-in time
    search_fields = ('username', 'email', 'first_name', 'last_name')  # Search fields

    def is_online_display(self, obj):
        """Display whether the user is online based on last_logged_in."""
        return obj.is_online()  # Use the is_online method from User model
    is_online_display.short_description = 'Online Status'  # Custom header for the column

    def allow_tagging(self, obj):
        return obj.tag_settings.allow_tagging
    allow_tagging.short_description = 'Allow Tagging'


admin.site.register(User, UserAdmin)  # Register the new User admin


class NotificationAdminForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = '__all__'
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3}),
            'link': forms.URLInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        if not user:
            raise forms.ValidationError("You must specify a user.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = self.cleaned_data.get("user")
        title = self.cleaned_data.get("title")
        body = self.cleaned_data.get("body")
        link = self.cleaned_data.get("link")
        userids = [user.id]
        NotificationService.send_notification_to_userids_admin(title, body, userids, link)
        if commit:
            instance.save()
        return instance

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationAdminForm
    list_display = ('colored_title', 'user_link', 'truncated_body', 'timestamp', 'read_status', 'link_display')
    list_filter = ('read', 'timestamp')
    search_fields = ('title', 'body', 'user__username', 'user__email')
    readonly_fields = ('timestamp',)
    actions = ['mark_as_read', 'mark_as_unread', 'resend_notification']
    
    def colored_title(self, obj):
        color = '#007bff' if obj.read else '#dc3545'
        return format_html('<span style="color: {};">{}</span>', color, obj.title)
    colored_title.short_description = 'Title'
    
    def user_link(self, obj):
        url = reverse("admin:accounts_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def truncated_body(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    truncated_body.short_description = 'Body'
    
    def read_status(self, obj):
        return format_html('<img src="/static/admin/img/icon-{}.svg" alt="{}"/>', 
                           'yes' if obj.read else 'no', 
                           'Read' if obj.read else 'Unread')
    read_status.short_description = 'Read'
    
    def link_display(self, obj):
        if obj.link:
            return format_html('<a href="{}" target="_blank">View</a>', obj.link)
        return '-'
    link_display.short_description = 'Link'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(read=True)
        self.message_user(request, ngettext(
            '%d notification was successfully marked as read.',
            '%d notifications were successfully marked as read.',
            updated,
        ) % updated, messages.SUCCESS)
    mark_as_read.short_description = "Mark selected notifications as read"

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(read=False)
        self.message_user(request, ngettext(
            '%d notification was successfully marked as unread.',
            '%d notifications were successfully marked as unread.',
            updated,
        ) % updated, messages.SUCCESS)
    mark_as_unread.short_description = "Mark selected notifications as unread"
    
    def resend_notification(self, request, queryset):
        for notification in queryset:
            NotificationService.send_notification_to_userids_admin(
                notification.title, 
                notification.body, 
                [notification.user.id], 
                notification.link
            )
        self.message_user(request, ngettext(
            '%d notification was successfully resent.',
            '%d notifications were successfully resent.',
            queryset.count(),
        ) % queryset.count(), messages.SUCCESS)
    resend_notification.short_description = "Resend selected notifications"

    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'title', 'body', 'link')
        }),
        ('Status', {
            'fields': ('read', 'timestamp'),
        }),
    )

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'expires_at')
    search_fields = ('user__username', 'code')
    list_filter = ('created_at', 'expires_at')
    readonly_fields = ('created_at', 'expires_at')

    def user_link(self, obj):
        url = reverse("admin:accounts_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'

    def code_link(self, obj):
        return format_html('<a href="{}">{}</a>', obj.code, obj.code)
    code_link.short_description = 'Code'

    

