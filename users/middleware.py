from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class EmailVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.email_verified:
            # Allow access to logout and verification endpoints
            allowed_paths = [
                reverse('users:logout'),
                reverse('users:verification_sent'),
                reverse('users:resend_verification'),
            ]
            if not any(request.path.startswith(path) for path in allowed_paths):
                messages.warning(request, 'Please verify your email to access this page.')
                return redirect('users:verification_sent')
        return self.get_response(request)