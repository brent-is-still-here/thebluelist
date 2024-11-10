from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        redirect_field_name='next'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/'
    ), name='logout'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('verification-sent/', views.verification_sent, name='verification_sent'),
    path('verification-success/', views.verification_success, name='verification_success'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
]