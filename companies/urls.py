from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-business/', views.add_business, name='add_business'),
    path('api/', include('companies.api.urls')),
    path('business/<slug:slug>/', views.business_detail, name='business_detail'),
    path('edit-requests/', views.edit_requests, name='edit_requests'),
    path('filter-categories/', views.filter_categories, name='filter_categories'),
    path('review/', views.review_edit_requests, name='review_edit_requests'),
    path('review/<int:edit_request_id>/', views.review_edit_request, name='review_edit_request'),
    path('search/', views.business_search, name='business_search'),
    path('update/<int:business_id>/', views.submit_update, name='submit_update'),
]
