from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.business_search, name='business_search'),
    path('add-business/', views.add_business, name='add_business'),
    path('business/<slug:slug>/', views.business_detail, name='business_detail'),
    path('edit-requests/', views.edit_requests, name='edit_requests'),
    path('filter-categories/', views.filter_categories, name='filter_categories'),
    path('update/<int:business_id>/', views.submit_update, name='submit_update'),
    path('api/', include('companies.api.urls')),
]
