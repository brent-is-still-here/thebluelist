from django.urls import path
from . import views

urlpatterns = [
    path('', views.security_landing, name='security_landing'),
    path('browse/', views.security_browse, name='security_browse'),
]
