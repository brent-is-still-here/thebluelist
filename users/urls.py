from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('get-involved/', views.get_involved, name='get_involved'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/'
    ), name='logout'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('verification-sent/', views.verification_sent, name='verification_sent'),
    path('verification-success/', views.verification_success, name='verification_success'),
    path('recovery-key/', views.show_recovery_key, name='show_recovery_key'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('reset-password/', views.reset_password, name='reset_password'),
]