# middleware.py
from django.utils import timezone

class UpdateLastActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Update last_active only if the user is authenticated
            request.user.last_active = timezone.now()
            request.user.save(update_fields=['last_active'])
        response = self.get_response(request)
        return response
