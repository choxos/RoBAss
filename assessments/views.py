from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
import json
import uuid

from .models import (
    AssessmentTool, Domain, SignallingQuestion, Project, Study, 
    Assessment, DomainAssessment, QuestionResponse
)
from .forms import ProjectForm, StudyForm
from .utils import generate_visualization, export_assessments_csv


def home_view(request):
    """Home page with overview of RoBAss"""
    context = {
        'title': 'Risk of Bias Assessment Tool'
    }
    return render(request, 'assessments/home.html', context)


@login_required
def dashboard_view(request):
    """User dashboard with projects and recent activity"""
    projects = Project.objects.filter(user=request.user).annotate(
        study_count=Count('studies'),
        assessment_count=Count('studies__assessments')
    ).order_by('-updated_at')
    
    recent_assessments = Assessment.objects.filter(
        study__project__user=request.user
    ).select_related('study', 'assessment_tool').order_by('-updated_at')[:10]
    
    # Statistics
    total_projects = projects.count()
    total_studies = Study.objects.filter(project__user=request.user).count()
    total_assessments = Assessment.objects.filter(study__project__user=request.user).count()
    completed_assessments = Assessment.objects.filter(
        study__project__user=request.user, status='completed'
    ).count()
    
    context = {
        'projects': projects,
        'recent_assessments': recent_assessments,
        'total_projects': total_projects,
        'total_studies': total_studies,
        'total_assessments': total_assessments,
        'completed_assessments': completed_assessments,
        'title': 'Dashboard'
    }
    return render(request, 'assessments/dashboard.html', context)


def tool_selection_view(request):
    """Tool selection page for starting new assessment"""
    tools = AssessmentTool.objects.filter(is_active=True).prefetch_related('domains')
    
    context = {
        'tools': tools,
        'title': 'Select Assessment Tool'
    }
    return render(request, 'assessments/tool_selection.html', context)


@login_required
def project_list_view(request):
    """List all user's projects with search and pagination"""
    query = request.GET.get('q', '')
    projects = Project.objects.filter(user=request.user).annotate(
        study_count=Count('studies'),
        assessment_count=Count('studies__assessments')
    )
    
    if query:
        projects = projects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    projects = projects.order_by('-updated_at')
    
    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'title': 'My Projects'
    }
    return render(request, 'assessments/project_list.html', context)


@login_required
def project_create_view(request):
    """Create new project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('assessments:project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'title': 'Create New Project'
    }
    return render(request, 'assessments/project_form.html', context)


@login_required
def project_detail_view(request, project_id):
    """Project detail with studies and assessments"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    studies = project.studies.all().annotate(
        assessment_count=Count('assessments')
    ).order_by('-updated_at')
    
    # Recent assessments for this project
    recent_assessments = Assessment.objects.filter(
        study__project=project
    ).select_related('study', 'assessment_tool').order_by('-updated_at')[:5]
    
    context = {
        'project': project,
        'studies': studies,
        'recent_assessments': recent_assessments,
        'title': project.name
    }
    return render(request, 'assessments/project_detail.html', context)


@login_required
def study_create_view(request, project_id):
    """Add new study to project"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    if request.method == 'POST':
        form = StudyForm(request.POST)
        if form.is_valid():
            study = form.save(commit=False)
            study.project = project
            study.save()
            messages.success(request, f'Study "{study.title}" added successfully!')
            return redirect('assessments:project_detail', project_id=project.id)
    else:
        form = StudyForm()
    
    context = {
        'form': form,
        'project': project,
        'title': f'Add Study to {project.name}'
    }
    return render(request, 'assessments/study_form.html', context)


@login_required
def assessment_create_view(request, study_id, tool_name):
    """Start new assessment for a study"""
    study = get_object_or_404(Study, id=study_id, project__user=request.user)
    tool = get_object_or_404(AssessmentTool, name=tool_name, is_active=True)
    
    # Check if assessment already exists
    existing_assessment = Assessment.objects.filter(study=study, assessment_tool=tool).first()
    if existing_assessment:
        messages.info(request, 'Assessment already exists. Continuing with existing assessment.')
        return redirect('assessments:assessment_detail', assessment_id=existing_assessment.id)
    
    # Create new assessment
    assessment = Assessment.objects.create(
        study=study,
        assessment_tool=tool,
        assessor_name=request.user.get_full_name() or request.user.username,
        assessor_email=request.user.email
    )
    
    # Create domain assessments
    domains = tool.domains.all()
    for domain in domains:
        DomainAssessment.objects.create(
            assessment=assessment,
            domain=domain
        )
    
    messages.success(request, f'New {tool.display_name} assessment started!')
    return redirect('assessments:assessment_detail', assessment_id=assessment.id)


@login_required
def assessment_detail_view(request, assessment_id):
    """Assessment form with signalling questions"""
    assessment = get_object_or_404(
        Assessment, 
        id=assessment_id, 
        study__project__user=request.user
    )
    
    # Get domain assessments with questions
    domain_assessments = assessment.domain_assessments.select_related(
        'domain'
    ).prefetch_related(
        'domain__signalling_questions',
        'question_responses__signalling_question'
    ).order_by('domain__order')
    
    # Prepare data structure for template
    assessment_data = []
    for domain_assessment in domain_assessments:
        questions = domain_assessment.domain.signalling_questions.all().order_by('order')
        responses = {qr.signalling_question_id: qr for qr in domain_assessment.question_responses.all()}
        
        questions_data = []
        for question in questions:
            response = responses.get(question.id)
            questions_data.append({
                'question': question,
                'response': response
            })
        
        assessment_data.append({
            'domain_assessment': domain_assessment,
            'questions': questions_data
        })
    
    context = {
        'assessment': assessment,
        'assessment_data': assessment_data,
        'title': f'{assessment.assessment_tool.display_name} Assessment'
    }
    return render(request, 'assessments/assessment_detail.html', context)


def guest_access_view(request):
    """Guest access landing page"""
    tools = AssessmentTool.objects.filter(is_active=True)
    
    if request.method == 'POST':
        # Create guest session and redirect to tool selection
        if not request.session.session_key:
            request.session.create()
        messages.info(request, 'You are using RoBAss as a guest. Your data will be stored temporarily.')
        return redirect('assessments:tool_selection')
    
    context = {
        'tools': tools,
        'title': 'Guest Access'
    }
    return render(request, 'assessments/guest_access.html', context)


def about_view(request):
    """About page with tool information"""
    context = {
        'title': 'About RoBAss'
    }
    return render(request, 'assessments/about.html', context)


@require_http_methods(["POST"])
@login_required
def save_response_view(request, assessment_id):
    """Save signalling question response via AJAX"""
    try:
        data = json.loads(request.body)
        assessment = get_object_or_404(
            Assessment, 
            id=assessment_id, 
            study__project__user=request.user
        )
        
        domain_id = data.get('domain_id')
        question_id = data.get('question_id')
        response = data.get('response')
        justification = data.get('justification', '')
        
        domain_assessment = get_object_or_404(
            DomainAssessment,
            assessment=assessment,
            domain_id=domain_id
        )
        
        signalling_question = get_object_or_404(
            SignallingQuestion,
            id=question_id,
            domain_id=domain_id
        )
        
        # Update or create response
        question_response, created = QuestionResponse.objects.update_or_create(
            domain_assessment=domain_assessment,
            signalling_question=signalling_question,
            defaults={
                'response': response,
                'justification': justification
            }
        )
        
        # Update assessment timestamp
        assessment.updated_at = timezone.now()
        assessment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Response saved successfully'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
def export_csv_view(request, project_id):
    """Export project assessments as CSV"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{project.name}_assessments.csv"'
    
    # Generate CSV content
    csv_content = export_assessments_csv(project)
    response.write(csv_content)
    
    return response
