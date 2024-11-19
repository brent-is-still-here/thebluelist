from django.urls import path
from . import views

app_name = 'relocation_planner'

urlpatterns = [
    path('', views.LandingView.as_view(), name='landing'),
    path('countries/', views.CountryListView.as_view(), name='country-list'),
]