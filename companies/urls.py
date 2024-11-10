from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.business_search, name='business_search'),
    path('add-business/', views.add_business, name='add_business'),
    path('edit-requests/', views.edit_requests, name='edit_requests'),
    path('api/', include('companies.api.urls')),
]
