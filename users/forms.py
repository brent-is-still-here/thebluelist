from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import User, HashedEmail

User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
        'placeholder': 'Password'
    }))
    remember_me = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        user = self.get_user()
        
        if user and not user.email_verified:
            raise forms.ValidationError(
                "Please verify your email address before logging in."
            )
        
        return cleaned_data

class PasswordResetForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
        'placeholder': 'Username'
    }))
    recovery_key = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
        'placeholder': 'Recovery Key'
    }))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
        'placeholder': 'New Password'
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
        'placeholder': 'Confirm New Password'
    }))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password1') != cleaned_data.get('new_password2'):
            raise forms.ValidationError("The two password fields didn't match.")
        return cleaned_data

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        
        # Check if the email hash is blocked
        email_hash = HashedEmail.hash_email(email)
        try:
            hashed_email = HashedEmail.objects.get(email_hash=email_hash)
            if hashed_email.is_blocked:
                raise forms.ValidationError(
                    "This email address cannot be used for registration. Please contact support if you think this is an error."
                )
            
            # Optional: Check for suspicious activity
            if hashed_email.get_total_users_count() >= settings.MAX_ACCOUNTS_PER_EMAIL:
                raise forms.ValidationError(
                    "Maximum number of accounts for this email has been reached."
                )
        except HashedEmail.DoesNotExist:
            pass
        
        return email
    