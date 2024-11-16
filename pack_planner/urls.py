from django.urls import path
from . import views

urlpatterns = [
    path('', views.pack_landing, name='pack_landing'),
    path('assessment/', views.pack_assessment, name='pack_assessment'),
    path('assessment/results/', views.pack_assessment_results, name='pack_assessment_results'),
    path('browse/', views.pack_browse, name='pack_browse'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('print/', views.print_checklist, name='print_checklist'),
]