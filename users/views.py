
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_http_methods
import secrets
from .forms import LoginForm, SignupForm
from .models import User

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Handle remember me
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
                
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email_verified = False
            user.verification_token = secrets.token_urlsafe(32)
            user.save()
            
            # Send verification email
            verification_url = request.build_absolute_uri(
                reverse('users:verify_email', args=[user.verification_token])
            )
            
            send_mail(
                'Verify your email for The Blue List',
                f'Click this link to verify your email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            return redirect('users:verification_sent')
    else:
        form = SignupForm()
    
    return render(request, 'users/signup.html', {'form': form})

def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token, email_verified=False)
        user.email_verified = True
        user.verification_token = ''
        user.save()
        messages.success(request, 'Your email has been verified. You can now log in.')
        return redirect('users:verification_success')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('users:login')

def verification_sent(request):
    return render(request, 'users/verification_sent.html')

def verification_success(request):
    return render(request, 'users/verification_success.html')

@login_required
def resend_verification(request):
    if not request.user.email_verified:
        request.user.verification_token = secrets.token_urlsafe(32)
        request.user.save()
        
        verification_url = request.build_absolute_uri(
            reverse('users:verify_email', args=[request.user.verification_token])
        )
        
        send_mail(
            'Verify your email for The Blue List',
            f'Click this link to verify your email: {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        
        messages.success(request, 'Verification email has been resent.')
    return redirect('users:verification_sent')
