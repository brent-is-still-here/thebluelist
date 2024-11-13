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
import logging
from .forms import LoginForm, PasswordResetForm, SignupForm
from .models import RecoveryKey, User, HashedEmail
from .services.mail import EmailService

logger = logging.getLogger(__name__)
email_service = EmailService()

def get_involved(request):
    return render(request, 'users/get_involved.html')

def login_view(request):
    if request.user.is_authenticated:
        # Check if they need to see their recovery key
        if not request.user.recovery_key_viewed:
            return redirect('users:show_recovery_key')
        return redirect('home')
        
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Check if user's hashed_email is blocked
            if user.hashed_email and user.hashed_email.is_blocked:
                messages.error(request, 'This account has been disabled due to suspicious activity.')
                return render(request, 'users/login.html', {'form': form})
            
            login(request, user)
            user.update_last_login()
            
            # Handle remember me
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            
            # If this is their first time logging in, generate recovery key and redirect
            if not user.recovery_key_viewed:
                # Associate with HashedEmail if not already done
                if not user.hashed_email and user.email:
                    user.hashed_email = HashedEmail.get_or_create_hash(user.email)
                    user.save()

                recovery_key = RecoveryKey.generate_recovery_key()
                recovery_key_obj = RecoveryKey(user=user)
                recovery_key_obj.encrypt_recovery_key(recovery_key)
                recovery_key_obj.save()
                
                # Store the plain recovery key in session for display
                request.session['recovery_key'] = recovery_key
                
                return redirect('users:show_recovery_key')
                
            next_url = request.GET.get('next', 'home')
            logger.info(f"User {user.username} logged in successfully")
            return redirect(next_url)
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})

@login_required
@require_http_methods(['POST'])
def logout_view(request):
    username = request.user.username
    logout(request)
    logger.info(f"User {username} logged out successfully")
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def resend_verification(request):
    if not request.user.email_verified:
        try:
            request.user.verification_token = secrets.token_urlsafe(32)
            request.user.save()
            
            verification_url = request.build_absolute_uri(
                reverse('users:verify_email', args=[request.user.verification_token])
            )
            
            success, message_id = email_service.send_verification_email(
                request.user, 
                verification_url
            )
            
            if success:
                logger.info(f"Verification email resent successfully to {request.user.email}")
                messages.success(request, 'Verification email has been resent.')
            else:
                logger.error(f"Failed to resend verification email to {request.user.email}")
                messages.error(request, 'Failed to send verification email. Please try again.')
        except Exception as e:
            logger.error(f"Error in resend_verification: {str(e)}", exc_info=True)
            messages.error(request, 'An error occurred. Please try again.')
            
    return redirect('users:verification_sent')

def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(username=form.cleaned_data['username'])
                recovery_key_obj = RecoveryKey.objects.get(user=user)
                
                if recovery_key_obj.verify_recovery_key(form.cleaned_data['recovery_key']):
                    user.set_password(form.cleaned_data['new_password1'])
                    user.save()
                    messages.success(request, 'Password reset successfully. You can now log in.')
                    return redirect('users:login')
                else:
                    messages.error(request, 'Invalid recovery key.')
            except (User.DoesNotExist, RecoveryKey.DoesNotExist):
                messages.error(request, 'Invalid username or recovery key.')
    else:
        form = PasswordResetForm()
    
    return render(request, 'users/reset_password.html', {'form': form})

@login_required
def show_recovery_key(request):
    # Only show recovery key if they haven't seen it yet
    if request.user.recovery_key_viewed:
        messages.error(request, 'Recovery key has already been viewed.')
        return redirect('home')
    
    recovery_key = request.session.get('recovery_key')
    if not recovery_key:
        messages.error(request, 'Recovery key not found.')
        return redirect('home')
    
    if request.method == 'POST':
        # Mark recovery key as viewed and purge email
        request.user.recovery_key_viewed = True
        request.user.email_purged = True
        request.user.email = ''  # Purge email
        request.user.save()
        
        # Remove recovery key from session
        del request.session['recovery_key']
        
        messages.success(request, 'Your recovery key has been saved and your email has been purged.')
        return redirect('home')
    
    return render(request, 'users/show_recovery_key.html', {
        'recovery_key': recovery_key
    })

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.email_verified = False
                user.verification_token = secrets.token_urlsafe(32)
                user.save()
                
                verification_url = request.build_absolute_uri(
                    reverse('users:verify_email', args=[user.verification_token])
                )
                
                success, message_id = email_service.send_verification_email(
                    user, 
                    verification_url
                )
                
                if success:
                    logger.info(f"User {user.username} created and verification email sent")
                    messages.success(request, 
                        'Account created successfully. Please check your email to verify your account.')
                else:
                    logger.error(f"Failed to send verification email to new user {user.email}")
                    messages.warning(request, 
                        'Account created but we could not send the verification email. '
                        'Please use the resend verification option.')
                
                return redirect('users:verification_sent')
            except Exception as e:
                logger.error(f"Error in signup process: {str(e)}", exc_info=True)
                messages.error(request, 'An error occurred. Please try again.')
        else:
            logger.warning(f"Invalid signup form submission: {form.errors}")
    else:
        form = SignupForm()
    
    return render(request, 'users/signup.html', {'form': form})

def verification_sent(request):
    return render(request, 'users/verification_sent.html')

def verification_success(request):
    return render(request, 'users/verification_success.html')

def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token, email_verified=False)
        user.email_verified = True
        user.verification_token = ''
        user.save()
        logger.info(f"Email verified successfully for user {user.username}")
        messages.success(request, 'Your email has been verified. You can now log in.')
        return redirect('users:verification_success')
    except User.DoesNotExist:
        logger.warning(f"Invalid verification attempt with token: {token}")
        messages.error(request, 'Invalid verification link.')
        return redirect('users:login')
