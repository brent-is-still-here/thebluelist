from django.urls import path
from . import views

app_name = 'safety_at_home'

urlpatterns = [
    path('', views.safety_at_home_landing, name='safety_at_home_landing'),
]