from django.urls import path
from pack_planner import views

urlpatterns = [
    path('', views.pack_landing, name='pack_landing'),
    path('assessment/', views.pack_assessment, name='pack_assessment'),
    path('assessment/results/', views.pack_assessment_results, name='pack_assessment_results'),
    path('browse/', views.pack_browse, name='pack_browse'),
    path('data-upload/', views.data_upload, name='pack_upload'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('update-item-status/', views.update_item_status, name='update_item_status'),
    path('print/', views.print_checklist, name='print_checklist'),
]
