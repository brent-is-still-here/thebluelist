from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', include('companies.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace='users')),
    path('login/', auth_views.LoginView.as_view(template_name='companies/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('securityonline/', include('online_security.urls')),
]
