from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    # Home and main pages
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('guest/', views.guest_access_view, name='guest_access'),
    
    # Tool selection
    path('tools/', views.tool_selection_view, name='tool_selection'),
    
    # Project management
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/new/', views.project_create_view, name='project_create'),
    path('projects/<uuid:project_id>/', views.project_detail_view, name='project_detail'),
    path('projects/<uuid:project_id>/export/csv/', views.export_csv_view, name='export_csv'),
    
    # Study management
    path('projects/<uuid:project_id>/studies/new/', views.study_create_view, name='study_create'),
    
    # Assessment management
    path('studies/<int:study_id>/assess/<str:tool_name>/', views.assessment_create_view, name='assessment_create'),
    path('assessments/<int:assessment_id>/', views.assessment_detail_view, name='assessment_detail'),
    path('assessments/<int:assessment_id>/save/', views.save_response_view, name='save_response'),
]
