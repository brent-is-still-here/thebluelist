from django.urls import path
from . import views

urlpatterns = [
    path('', views.security_landing, name='security_landing'),
    path('assessment/', views.security_assessment, name='security_assessment'),
    path('assessment/results/', views.security_assessment_results, name='security_assessment_results'),
    path('browse/', views.security_browse, name='security_browse'),
    path('recommendation/<int:pk>/', views.security_recommendation_detail, name='security_recommendation_detail'),
]
