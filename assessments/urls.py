from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    # Home and main pages
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('tutorial/', views.tutorial_view, name='tutorial'),
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
    
    # Guest workflows
    path('guest/project/new/', views.guest_project_create_view, name='guest_project_create'),
    path('guest/projects/<uuid:project_id>/', views.guest_project_detail_view, name='guest_project_detail'),
    path('guest/projects/<uuid:project_id>/studies/<str:tool_name>/', views.guest_study_create_view, name='guest_study_create'),
    path('guest/assessments/<int:assessment_id>/', views.guest_assessment_detail_view, name='guest_assessment_detail'),
    path('guest/assessments/<int:assessment_id>/save/', views.guest_save_response_view, name='guest_save_response'),
]
