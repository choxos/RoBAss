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
import os

from .models import (
    AssessmentTool, Domain, SignallingQuestion, Project, Study, 
    Assessment, DomainAssessment, QuestionResponse, StudyDocument, LLMModel, LLMAssessment
)
from .forms import ProjectForm, StudyForm
from .utils import generate_visualization, export_assessments_csv
from .rob2_engine import calculate_rob2_assessment
from .robins_e_engine import ROBINSEEngine


def calculate_automatic_robins_e_assessment(assessment):
    """Calculate automatic ROBINS-E assessment from user responses"""
    # Get all question responses grouped by domain
    question_responses = QuestionResponse.objects.filter(
        domain_assessment__assessment=assessment
    ).select_related('signalling_question', 'domain_assessment__domain')
    
    # Group responses by domain
    domain_responses = {}
    for qr in question_responses:
        domain_order = qr.domain_assessment.domain.order
        domain_key = f'domain_{domain_order}'
        
        if domain_key not in domain_responses:
            domain_responses[domain_key] = {}
        
        # Map question text to response (ROBINS-E uses question text as keys)
        question_text = qr.signalling_question.identifier or qr.signalling_question.text
        domain_responses[domain_key][question_text] = qr.response
    
    # Initialize ROBINS-E engine
    try:
        robins_e_engine = ROBINSEEngine()
        
        # Calculate assessment using ROBINS-E engine
        if len(domain_responses) >= 3:  # Minimum domains for meaningful assessment
            results = robins_e_engine.complete_assessment(domain_responses)
            
            # Update assessment overall bias
            if 'overall' in results and 'overall_risk' in results['overall']:
                overall_risk_mapping = {
                    'Low risk of bias (except for concerns about uncontrolled confounding)': 'Low risk',
                    'Some concerns': 'Some concerns',
                    'High risk of bias': 'High risk',
                    'Very high risk of bias': 'Very high risk'
                }
                mapped_risk = overall_risk_mapping.get(results['overall']['overall_risk'], results['overall']['overall_risk'])
                assessment.overall_bias = mapped_risk
                assessment.save()
            
            return results
    except Exception as e:
        print(f"Error calculating ROBINS-E assessment: {str(e)}")
        return None
    
    return None


def calculate_automatic_rob2_assessment(assessment):
    """Calculate automatic RoB 2.0 assessment from user responses"""
    # Get all question responses
    responses = {}
    question_responses = QuestionResponse.objects.filter(
        domain_assessment__assessment=assessment
    ).select_related('signalling_question', 'domain_assessment__domain')
    
    for qr in question_responses:
        domain_order = qr.domain_assessment.domain.order
        question_order = qr.signalling_question.order
        question_key = f"{domain_order}.{question_order}"
        
        # Map response to RoB 2.0 format
        response_mapping = {
            'yes': 'Y',
            'probably_yes': 'PY',
            'probably_no': 'PN',
            'no': 'N',
            'no_information': 'NI',
            'not_applicable': 'NA'
        }
        
        if qr.response in response_mapping:
            responses[question_key] = response_mapping[qr.response]
    
    # Calculate assessment using RoB 2.0 engine
    if len(responses) >= 22:  # Minimum questions for RoB 2.0
        results = calculate_rob2_assessment(responses)
        
        # Update assessment overall bias
        if 'overall' in results:
            overall_risk_mapping = {
                'Low': 'Low risk',
                'Some concerns': 'Some concerns', 
                'High': 'High risk'
            }
            mapped_risk = overall_risk_mapping.get(results['overall']['risk'], results['overall']['risk'])
            assessment.overall_bias = mapped_risk
            assessment.save()
        
        return results
    
    return None


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


def guest_project_create_view(request):
    """Create project for guest users with tool selection"""
    tool_name = request.GET.get('tool')
    tool = None
    if tool_name:
        tool = get_object_or_404(AssessmentTool, name=tool_name, is_active=True)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = None  # Guest project
            
            # Create or get session key
            if not request.session.session_key:
                request.session.create()
            project.session_key = request.session.session_key
            project.save()
            
            messages.success(request, f'Project "{project.name}" created successfully!')
            
            # If tool was selected, redirect to study creation with tool context
            if tool:
                return redirect('assessments:guest_study_create', project_id=project.id, tool_name=tool.name)
            else:
                return redirect('assessments:guest_project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'tool': tool,
        'title': f'Create Project - {tool.display_name}' if tool else 'Create Project (Guest)'
    }
    return render(request, 'assessments/guest_project_form.html', context)


def guest_project_detail_view(request, project_id):
    """Guest project detail view"""
    if not request.session.session_key:
        messages.error(request, 'Session expired. Please start a new guest session.')
        return redirect('assessments:guest_access')
    
    project = get_object_or_404(
        Project, 
        id=project_id, 
        session_key=request.session.session_key,
        user=None
    )
    
    studies = project.studies.all().annotate(
        assessment_count=Count('assessments')
    ).order_by('-updated_at')
    
    context = {
        'project': project,
        'studies': studies,
        'title': f'{project.name} (Guest)'
    }
    return render(request, 'assessments/guest_project_detail.html', context)


def guest_study_create_view(request, project_id, tool_name):
    """Create study for guest project with direct tool selection"""
    if not request.session.session_key:
        messages.error(request, 'Session expired. Please start a new guest session.')
        return redirect('assessments:guest_access')
    
    project = get_object_or_404(
        Project, 
        id=project_id, 
        session_key=request.session.session_key,
        user=None
    )
    tool = get_object_or_404(AssessmentTool, name=tool_name, is_active=True)
    
    if request.method == 'POST':
        form = StudyForm(request.POST)
        if form.is_valid():
            study = form.save(commit=False)
            study.project = project
            study.save()
            
            # Create assessment immediately
            assessment = Assessment.objects.create(
                study=study,
                assessment_tool=tool,
                assessor_name='Guest User',
                assessor_email=''
            )
            
            # Create domain assessments
            domains = tool.domains.all()
            for domain in domains:
                DomainAssessment.objects.create(
                    assessment=assessment,
                    domain=domain
                )
            
            messages.success(request, f'Study created and {tool.display_name} assessment started!')
            return redirect('assessments:guest_assessment_detail', assessment_id=assessment.id)
    else:
        form = StudyForm()
    
    context = {
        'form': form,
        'project': project,
        'tool': tool,
        'title': f'Add Study - {tool.display_name}'
    }
    return render(request, 'assessments/guest_study_form.html', context)


def guest_assessment_detail_view(request, assessment_id):
    """Guest assessment detail view"""
    if not request.session.session_key:
        messages.error(request, 'Session expired. Please start a new guest session.')
        return redirect('assessments:guest_access')
    
    assessment = get_object_or_404(
        Assessment,
        id=assessment_id,
        study__project__session_key=request.session.session_key,
        study__project__user=None
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
        'is_guest': True,
        'title': f'{assessment.assessment_tool.display_name} Assessment (Guest)'
    }
    return render(request, 'assessments/assessment_detail.html', context)


def about_view(request):
    """About page with tool information"""
    context = {
        'title': 'About RoBAss'
    }
    return render(request, 'assessments/about.html', context)


def tutorial_view(request):
    """Tutorial page with comprehensive guide"""
    context = {
        'title': 'Tutorial & Guide'
    }
    return render(request, 'assessments/tutorial.html', context)


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
        
        # Calculate automatic assessment based on tool type
        auto_assessment_results = None
        if assessment.assessment_tool.name == 'rob2_parallel':
            try:
                auto_assessment_results = calculate_automatic_rob2_assessment(assessment)
            except Exception as e:
                # Log error but don't fail the response saving
                print(f"Error calculating RoB 2.0 automatic assessment: {str(e)}")
        elif assessment.assessment_tool.name == 'robins_e':
            try:
                auto_assessment_results = calculate_automatic_robins_e_assessment(assessment)
            except Exception as e:
                # Log error but don't fail the response saving
                print(f"Error calculating ROBINS-E automatic assessment: {str(e)}")
        
        response_data = {
            'success': True,
            'message': 'Response saved successfully'
        }
        
        if auto_assessment_results:
            response_data['auto_assessment'] = auto_assessment_results
        
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_http_methods(["POST"])
@login_required
def calculate_domain_assessment_view(request, assessment_id):
    """Calculate real-time domain assessment for RoB 2.0"""
    try:
        data = json.loads(request.body)
        assessment = get_object_or_404(
            Assessment, 
            id=assessment_id, 
            study__project__user=request.user
        )
        
        if assessment.assessment_tool.name not in ['rob2_parallel', 'robins_e']:
            return JsonResponse({
                'success': False,
                'message': 'Real-time calculation available for RoB 2.0 and ROBINS-E only'
            })
        
        domain_id = data.get('domain_id')
        responses = data.get('responses', {})
        
        domain = get_object_or_404(Domain, id=domain_id)
        domain_order = domain.order
        
        domain_result = None
        
        # Handle different assessment tools
        if assessment.assessment_tool.name == 'rob2_parallel':
            # Map responses to RoB 2.0 format
            response_mapping = {
                'yes': 'Y',
                'probably_yes': 'PY',
                'probably_no': 'PN',
                'no': 'N',
                'no_information': 'NI',
                'not_applicable': 'NA'
            }
            
            # Convert responses to algorithm format
            algorithm_responses = {}
            for question_id, response in responses.items():
                question = SignallingQuestion.objects.get(id=question_id)
                question_order = question.order
                question_key = f"{domain_order}.{question_order}"
                if response in response_mapping:
                    algorithm_responses[question_key] = response_mapping[response]
            
            # Calculate domain assessment for RoB 2.0
            if domain_order == 1 and len(algorithm_responses) >= 3:
                # Domain 1: Randomization
                if all(key in algorithm_responses for key in ['1.1', '1.2', '1.3']):
                    from .rob2_engine import assess_domain_1_randomization
                    risk, reasoning = assess_domain_1_randomization(
                        algorithm_responses['1.1'],
                        algorithm_responses['1.2'],
                        algorithm_responses['1.3']
                    )
                    domain_result = {'risk': risk, 'reasoning': reasoning}
                    
            elif domain_order == 2 and len(algorithm_responses) >= 7:
                # Domain 2: Deviations
                if all(key in algorithm_responses for key in ['2.1', '2.2', '2.3', '2.4', '2.5', '2.6', '2.7']):
                    from .rob2_engine import assess_domain_2_deviations
                    risk, reasoning, details = assess_domain_2_deviations(
                        algorithm_responses['2.1'],
                        algorithm_responses['2.2'],
                        algorithm_responses['2.3'],
                        algorithm_responses['2.4'],
                        algorithm_responses['2.5'],
                        algorithm_responses['2.6'],
                        algorithm_responses['2.7']
                    )
                    domain_result = {'risk': risk, 'reasoning': reasoning}
                    
            elif domain_order == 3 and len(algorithm_responses) >= 4:
                # Domain 3: Missing data
                if all(key in algorithm_responses for key in ['3.1', '3.2', '3.3', '3.4']):
                    from .rob2_engine import assess_domain_3_missing_data
                    risk, reasoning = assess_domain_3_missing_data(
                        algorithm_responses['3.1'],
                        algorithm_responses['3.2'],
                        algorithm_responses['3.3'],
                        algorithm_responses['3.4']
                    )
                    domain_result = {'risk': risk, 'reasoning': reasoning}
                    
            elif domain_order == 4 and len(algorithm_responses) >= 5:
                # Domain 4: Outcome measurement
                if all(key in algorithm_responses for key in ['4.1', '4.2', '4.3', '4.4', '4.5']):
                    from .rob2_engine import assess_domain_4_outcome_measurement
                    risk, reasoning = assess_domain_4_outcome_measurement(
                        algorithm_responses['4.1'],
                        algorithm_responses['4.2'],
                        algorithm_responses['4.3'],
                        algorithm_responses['4.4'],
                        algorithm_responses['4.5']
                    )
                    domain_result = {'risk': risk, 'reasoning': reasoning}
                    
            elif domain_order == 5 and len(algorithm_responses) >= 3:
                # Domain 5: Selective reporting
                if all(key in algorithm_responses for key in ['5.1', '5.2', '5.3']):
                    from .rob2_engine import assess_domain_5_selective_reporting
                    risk, reasoning = assess_domain_5_selective_reporting(
                        algorithm_responses['5.1'],
                        algorithm_responses['5.2'],
                        algorithm_responses['5.3']
                    )
                    domain_result = {'risk': risk, 'reasoning': reasoning}
                    
        elif assessment.assessment_tool.name == 'robins_e':
            # Handle ROBINS-E domain assessment
            try:
                robins_e_engine = ROBINSEEngine()
                
                # Map responses to ROBINS-E format (using question text as keys)
                domain_responses = {}
                for question_id, response in responses.items():
                    question = SignallingQuestion.objects.get(id=question_id)
                    question_text = question.identifier or question.text
                    domain_responses[question_text] = response
                
                # Calculate domain assessment based on domain order
                domain_key = f'domain_{domain_order}'
                if domain_order == 1 and domain_responses:
                    result = robins_e_engine.assess_domain_1_confounding(domain_responses)
                    domain_result = {
                        'risk': result.get('risk_level', 'Unknown'),
                        'reasoning': result.get('pathway', 'No reasoning available')
                    }
                elif domain_order == 2 and domain_responses:
                    result = robins_e_engine.assess_domain_2_exposure_measurement(domain_responses)
                    domain_result = {
                        'risk': result.get('risk_level', 'Unknown'),
                        'reasoning': result.get('pathway', 'No reasoning available')
                    }
                elif domain_order == 3 and domain_responses:
                    result = robins_e_engine.assess_domain_3_selection(domain_responses)
                    domain_result = {
                        'risk': result.get('risk_level', 'Unknown'),
                        'reasoning': result.get('pathway', 'No reasoning available')
                    }
                elif domain_order == 4 and domain_responses:
                    result = robins_e_engine.assess_domain_4_post_exposure_interventions(domain_responses)
                    domain_result = {
                        'risk': result.get('risk_level', 'Unknown'),
                        'reasoning': result.get('pathway', 'No reasoning available')
                    }
                elif domain_order == 5 and domain_responses:
                    result = robins_e_engine.assess_domain_5_missing_data(domain_responses)
                    domain_result = {
                        'risk': result.get('risk_level', 'Unknown'),
                        'reasoning': result.get('pathway', 'No reasoning available')
                    }
                elif domain_order == 6 and domain_responses:
                    result = robins_e_engine.assess_domain_6_outcome_measurement(domain_responses)
                    domain_result = {
                        'risk': result.get('risk_level', 'Unknown'),
                        'reasoning': result.get('pathway', 'No reasoning available')
                    }
                elif domain_order == 7 and domain_responses:
                    result = robins_e_engine.assess_domain_7_reported_result(domain_responses)
                    domain_result = {
                        'risk': result.get('risk_level', 'Unknown'),
                        'reasoning': result.get('pathway', 'No reasoning available')
                    }
                    
            except Exception as e:
                print(f"Error calculating ROBINS-E domain assessment: {str(e)}")
                domain_result = None
        
        return JsonResponse({
            'success': True,
            'domain_result': domain_result
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_http_methods(["POST"])
def guest_save_response_view(request, assessment_id):
    """Save signalling question response via AJAX for guest users"""
    try:
        if not request.session.session_key:
            return JsonResponse({
                'success': False,
                'message': 'Session expired'
            }, status=400)
        
        data = json.loads(request.body)
        assessment = get_object_or_404(
            Assessment,
            id=assessment_id,
            study__project__session_key=request.session.session_key,
            study__project__user=None
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
def text_hints_view(request, assessment_id):
    """Get text hints from study documents for assessment"""
    assessment = get_object_or_404(
        Assessment, 
        id=assessment_id, 
        study__project__user=request.user
    )
    
    try:
        # Get the study document with extracted text
        study_doc = StudyDocument.objects.filter(
            study=assessment.study,
            document_type='full_text',
            extracted_text__isnull=False
        ).first()
        
        if not study_doc or not study_doc.extracted_text:
            return JsonResponse({
                'success': False,
                'message': 'No extracted text available'
            })
        
        # Analyze text for domain-specific content
        from .services.pdf_service import TextAnalyzer
        analyzer = TextAnalyzer(study_doc.extracted_text)
        
        return JsonResponse({
            'success': True,
            'randomization': analyzer.find_randomization_content(),
            'blinding': analyzer.find_blinding_content(),
            'missing_data': analyzer.find_missing_data_content(),
            'outcome_measurement': analyzer.find_outcome_measurement_content(),
            'selective_reporting': analyzer.find_selective_reporting_content()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


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


@login_required
def enhanced_study_create_view(request, project_id):
    """Enhanced study creation with PDF upload and metadata extraction"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    tool_name = request.GET.get('tool', 'rob2_parallel')  # Default to RoB 2
    tool = get_object_or_404(AssessmentTool, name=tool_name, is_active=True)
    
    if request.method == 'POST':
        # Handle PDF upload and metadata extraction
        pdf_file = request.FILES.get('pdf_file')
        pmid = request.POST.get('pmid', '').strip()
        doi = request.POST.get('doi', '').strip()
        assessment_type = request.POST.get('assessment_type')  # 'manual' or 'llm'
        
        if not pdf_file and not pmid and not doi:
            messages.error(request, 'Please upload a PDF file or provide a PMID/DOI.')
            return render(request, 'assessments/enhanced_study_create.html', {
                'project': project,
                'tool': tool,
                'title': f'Add Study - {tool.display_name}'
            })
        
        try:
            # Extract metadata first
            metadata = None
            if pmid or doi:
                from .services.metadata_service import MetadataExtractor
                extractor = MetadataExtractor()
                if pmid:
                    metadata = extractor.fetch_from_pmid(pmid)
                elif doi:
                    metadata = extractor.fetch_from_doi(doi)
            
            # Extract text from PDF if provided
            extracted_text = None
            if pdf_file:
                from .services.pdf_service import PDFProcessor
                processor = PDFProcessor()
                extracted_text = processor.extract_text(pdf_file)
                
                # If no metadata from PMID/DOI, try to extract from PDF
                if not metadata:
                    metadata = processor.extract_metadata(extracted_text)
            
            # Create study with extracted/provided metadata
            study_data = {
                'title': metadata.get('title', 'Study Title') if metadata else 'Study Title',
                'authors': metadata.get('authors', '') if metadata else '',
                'journal': metadata.get('journal', '') if metadata else '',
                'year': metadata.get('year') if metadata else None,
                'doi': metadata.get('doi', doi) if metadata else doi,
                'pmid': metadata.get('pmid', pmid) if metadata else pmid,
                'study_design': metadata.get('study_design', '') if metadata else '',
            }
            
            study = Study.objects.create(
                project=project,
                **study_data
            )
            
            # Save PDF document if uploaded
            if pdf_file:
                StudyDocument.objects.create(
                    study=study,
                    document_type='full_text',
                    title=f'Full Text - {study.title[:100]}',
                    file=pdf_file,
                    extracted_text=extracted_text or ''
                )
            
            # Create assessment
            assessment = Assessment.objects.create(
                study=study,
                assessment_tool=tool,
                assessor_name=request.user.get_full_name() or request.user.username,
                assessor_email=request.user.email
            )
            
            # Create domain assessments
            for domain in tool.domains.all():
                DomainAssessment.objects.create(
                    assessment=assessment,
                    domain=domain
                )
            
            # Handle LLM assessment if requested
            if assessment_type == 'llm' and extracted_text:
                try:
                    llm_result = perform_llm_assessment(assessment, extracted_text)
                    if llm_result:
                        messages.success(request, f'Study created successfully! LLM assessment completed with {llm_result.confidence_score:.2f} confidence.')
                    else:
                        messages.warning(request, 'Study created but LLM assessment failed. You can perform manual assessment.')
                except Exception as e:
                    messages.warning(request, f'Study created but LLM assessment failed: {str(e)}. You can perform manual assessment.')
            else:
                messages.success(request, f'Study "{study.title}" created successfully!')
            
            return redirect('assessments:assessment_detail', assessment_id=assessment.id)
            
        except Exception as e:
            messages.error(request, f'Error processing study: {str(e)}')
    
    # Available LLM models for selection
    llm_models = LLMModel.objects.filter(is_active=True).order_by('provider', 'display_name')
    
    context = {
        'project': project,
        'tool': tool,
        'llm_models': llm_models,
        'title': f'Add Study - {tool.display_name}'
    }
    return render(request, 'assessments/enhanced_study_create.html', context)


@login_required 
def study_metadata_view(request, study_id):
    """View to display and edit study metadata"""
    study = get_object_or_404(Study, id=study_id, project__user=request.user)
    
    if request.method == 'POST':
        # Update study metadata
        study.title = request.POST.get('title', study.title)
        study.authors = request.POST.get('authors', study.authors)
        study.journal = request.POST.get('journal', study.journal)
        study.year = request.POST.get('year') or study.year
        study.doi = request.POST.get('doi', study.doi)
        study.pmid = request.POST.get('pmid', study.pmid)
        study.study_design = request.POST.get('study_design', study.study_design)
        study.notes = request.POST.get('notes', study.notes)
        study.save()
        
        messages.success(request, 'Study metadata updated successfully!')
        return redirect('assessments:study_metadata', study_id=study.id)
    
    # Get associated documents
    documents = study.documents.all().order_by('-uploaded_at')
    
    context = {
        'study': study,
        'documents': documents,
        'title': f'Metadata - {study.title[:50]}'
    }
    return render(request, 'assessments/study_metadata.html', context)


@login_required
def enhanced_upload_view(request, project_id):
    """Step 1: Enhanced PDF upload with metadata extraction"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    tool_name = request.GET.get('tool', 'rob2_parallel')
    tool = get_object_or_404(AssessmentTool, name=tool_name, is_active=True)
    
    context = {
        'project': project,
        'tool': tool,
        'title': f'Upload Study - {tool.display_name}'
    }
    return render(request, 'assessments/enhanced_upload.html', context)


@login_required
def process_upload_view(request, project_id):
    """Step 2: Process uploaded PDF and metadata, show confirmation"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    tool_name = request.POST.get('tool') or request.GET.get('tool', 'rob2_parallel')
    tool = get_object_or_404(AssessmentTool, name=tool_name, is_active=True)
    
    if request.method != 'POST':
        return redirect('assessments:enhanced_upload', project_id=project.id)
    
    # Handle PDF upload and metadata extraction
    pdf_file = request.FILES.get('pdf_file')
    pmid = request.POST.get('pmid', '').strip()
    doi = request.POST.get('doi', '').strip()
    
    if not pdf_file and not pmid and not doi:
        messages.error(request, 'Please upload a PDF file or provide a PMID/DOI.')
        return redirect('assessments:enhanced_upload', project_id=project.id)
    
    try:
        # Extract metadata first
        metadata = None
        if pmid or doi:
            from .services.metadata_service import MetadataExtractor
            extractor = MetadataExtractor()
            if pmid:
                metadata = extractor.fetch_from_pmid(pmid)
            elif doi:
                metadata = extractor.fetch_from_doi(doi)
        
        # Extract text from PDF if provided
        extracted_text = None
        if pdf_file:
            from .services.pdf_service import PDFProcessor
            processor = PDFProcessor()
            extracted_text = processor.extract_text(pdf_file)
            
            # If no metadata from PMID/DOI, try to extract from PDF
            if not metadata:
                metadata = processor.extract_metadata(extracted_text)
        
        # Store data in session for next step
        session_data = {
            'project_id': str(project.id),
            'tool_name': tool_name,
            'metadata': metadata or {},
            'extracted_text': extracted_text or '',
            'pmid': pmid,
            'doi': doi,
            'has_pdf': bool(pdf_file)
        }
        
        # Store PDF file temporarily if uploaded
        if pdf_file:
            # Save PDF to a temporary location and store path in session
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            temp_filename = f"robass_temp_{request.user.id}_{project.id}_{tool_name}.pdf"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            with open(temp_path, 'wb+') as destination:
                for chunk in pdf_file.chunks():
                    destination.write(chunk)
            
            session_data['temp_pdf_path'] = temp_path
        
        request.session['upload_data'] = session_data
        
        context = {
            'project': project,
            'tool': tool,
            'metadata': metadata or {},
            'pmid': pmid,
            'doi': doi,
            'has_pdf': bool(pdf_file),
            'extracted_text_length': len(extracted_text) if extracted_text else 0,
            'title': f'Confirm Study Details - {tool.display_name}'
        }
        
        return render(request, 'assessments/confirm_metadata.html', context)
        
    except Exception as e:
        messages.error(request, f'Error processing upload: {str(e)}')
        return redirect('assessments:enhanced_upload', project_id=project.id)


@login_required
def select_assessment_method_view(request, project_id):
    """Step 3: Choose between LLM-assisted or manual assessment"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    # Get data from session
    session_data = request.session.get('upload_data')
    if not session_data or session_data.get('project_id') != str(project.id):
        messages.error(request, 'Session expired. Please upload your study again.')
        return redirect('assessments:project_detail', project_id=project.id)
    
    tool_name = session_data.get('tool_name', 'rob2_parallel')
    tool = get_object_or_404(AssessmentTool, name=tool_name, is_active=True)
    
    # Handle metadata updates from previous step
    if request.method == 'POST' and 'update_metadata' in request.POST:
        metadata = {
            'title': request.POST.get('title', ''),
            'authors': request.POST.get('authors', ''),
            'journal': request.POST.get('journal', ''),
            'year': request.POST.get('year') or None,
            'doi': request.POST.get('doi', ''),
            'pmid': request.POST.get('pmid', ''),
            'study_design': request.POST.get('study_design', ''),
        }
        session_data['metadata'] = metadata
        request.session['upload_data'] = session_data
    
    # Available LLM models
    llm_models = LLMModel.objects.filter(is_active=True).order_by('provider', 'display_name')
    
    context = {
        'project': project,
        'tool': tool,
        'metadata': session_data.get('metadata', {}),
        'has_pdf': session_data.get('has_pdf', False),
        'extracted_text_length': len(session_data.get('extracted_text', '')),
        'llm_models': llm_models,
        'title': f'Choose Assessment Method - {tool.display_name}'
    }
    
    return render(request, 'assessments/select_assessment_method.html', context)


@login_required
def create_study_with_assessment_view(request, project_id):
    """Step 4: Create study and assessment based on chosen method"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    # Get data from session
    session_data = request.session.get('upload_data')
    if not session_data or session_data.get('project_id') != str(project.id):
        messages.error(request, 'Session expired. Please upload your study again.')
        return redirect('assessments:project_detail', project_id=project.id)
    
    if request.method != 'POST':
        return redirect('assessments:select_assessment_method', project_id=project.id)
    
    tool_name = session_data.get('tool_name', 'rob2_parallel')
    tool = get_object_or_404(AssessmentTool, name=tool_name, is_active=True)
    
    assessment_method = request.POST.get('assessment_method', 'manual')  # 'manual' or 'llm'
    
    try:
        # Create study with metadata
        metadata = session_data.get('metadata', {})
        study_data = {
            'title': metadata.get('title', 'Study Title'),
            'authors': metadata.get('authors', ''),
            'journal': metadata.get('journal', ''),
            'year': metadata.get('year') or None,
            'doi': metadata.get('doi', ''),
            'pmid': metadata.get('pmid', ''),
            'study_design': metadata.get('study_design', ''),
        }
        
        study = Study.objects.create(
            project=project,
            **study_data
        )
        
        # Save PDF document if it was uploaded
        temp_pdf_path = session_data.get('temp_pdf_path')
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            from django.core.files import File
            from django.core.files.storage import default_storage
            
            with open(temp_pdf_path, 'rb') as f:
                StudyDocument.objects.create(
                    study=study,
                    document_type='full_text',
                    title=f'Full Text - {study.title[:100]}',
                    file=File(f, name=f'{study.title[:50]}.pdf'),
                    extracted_text=session_data.get('extracted_text', '')
                )
            
            # Clean up temporary file
            try:
                os.remove(temp_pdf_path)
            except:
                pass
        
        # Create assessment
        assessment = Assessment.objects.create(
            study=study,
            assessment_tool=tool,
            assessor_name=request.user.get_full_name() or request.user.username,
            assessor_email=request.user.email
        )
        
        # Create domain assessments
        for domain in tool.domains.all():
            DomainAssessment.objects.create(
                assessment=assessment,
                domain=domain
            )
        
        # Handle LLM assessment if requested
        if assessment_method == 'llm' and session_data.get('extracted_text'):
            try:
                llm_result = perform_llm_assessment(assessment, session_data.get('extracted_text'))
                if llm_result:
                    messages.success(request, 
                        f'Study created successfully! LLM assessment completed with '
                        f'{llm_result.confidence_score:.2f} confidence.')
                else:
                    messages.warning(request, 'Study created but LLM assessment failed. You can perform manual assessment.')
            except Exception as e:
                messages.warning(request, 
                    f'Study created but LLM assessment failed: {str(e)}. You can perform manual assessment.')
        else:
            messages.success(request, f'Study "{study.title}" created successfully!')
        
        # Clean up session data
        if 'upload_data' in request.session:
            del request.session['upload_data']
        
        return redirect('assessments:assessment_detail', assessment_id=assessment.id)
        
    except Exception as e:
        messages.error(request, f'Error creating study: {str(e)}')
        return redirect('assessments:select_assessment_method', project_id=project.id)


def perform_llm_assessment(assessment, extracted_text):
    """Perform LLM-based assessment using the extracted text"""
    try:
        # Get default LLM model or first available
        llm_model = LLMModel.objects.filter(is_active=True).first()
        if not llm_model:
            raise Exception('No active LLM model available')
        
        # Import LLM service and appropriate prompt templates based on tool
        from .services.llm_service import LLMService
        tool_name = assessment.assessment_tool.name
        
        llm_service = LLMService(llm_model)
        
        # Select appropriate prompt generator based on assessment tool
        if tool_name == 'robins_e':
            from .services.robins_e_llm_prompts import ROBINSEPromptTemplates
            prompt_generator = ROBINSEPromptTemplates()
            prompt = prompt_generator.generate_assessment_prompt(extracted_text)
        else:  # Default to RoB 2.0
            from .services.llm_prompts import RoB2PromptTemplates
            prompt_generator = RoB2PromptTemplates()
            prompt = prompt_generator.generate_assessment_prompt(extracted_text)
        
        # Get LLM response
        start_time = timezone.now()
        llm_response = llm_service.generate_assessment(prompt)
        processing_time = (timezone.now() - start_time).total_seconds()
        
        if not llm_response:
            raise Exception('Empty response from LLM')
        
        # Parse LLM response and create assessment responses
        if tool_name == 'robins_e':
            parsed_results = llm_service.parse_robins_e_response(llm_response)
        else:  # Default to RoB 2.0
            parsed_results = llm_service.parse_rob2_response(llm_response)
        
        # Save LLM assessment record
        llm_assessment = LLMAssessment.objects.create(
            assessment=assessment,
            llm_model=llm_model,
            prompt_used=prompt,
            raw_response=llm_response,
            parsed_results=parsed_results,
            confidence_score=parsed_results.get('confidence', 0.8),
            processing_time=processing_time
        )
        
        # Create question responses from LLM results
        response_mapping = {
            'Y': 'yes',
            'PY': 'probably_yes',
            'PN': 'probably_no',
            'N': 'no',
            'NI': 'no_information',
            'NA': 'not_applicable'
        }
        
        # Process each domain's responses
        for domain_key, domain_data in parsed_results.get('domains', {}).items():
            try:
                domain_order = int(domain_key.split('_')[1])  # Extract domain number
                domain = Domain.objects.get(
                    assessment_tool=assessment.assessment_tool,
                    order=domain_order
                )
                domain_assessment = DomainAssessment.objects.get(
                    assessment=assessment,
                    domain=domain
                )
                
                # Create responses for each signalling question
                for q_key, response_data in domain_data.get('questions', {}).items():
                    try:
                        question_order = int(q_key.split('_')[1])  # Extract question number
                        signalling_question = SignallingQuestion.objects.get(
                            domain=domain,
                            order=question_order
                        )
                        
                        llm_response_code = response_data.get('response', 'NI')
                        mapped_response = response_mapping.get(llm_response_code, 'no_information')
                        
                        QuestionResponse.objects.update_or_create(
                            domain_assessment=domain_assessment,
                            signalling_question=signalling_question,
                            defaults={
                                'response': mapped_response,
                                'justification': response_data.get('justification', '')
                            }
                        )
                    except (ValueError, SignallingQuestion.DoesNotExist) as e:
                        print(f"Error processing question {q_key}: {e}")
                        continue
                        
            except (ValueError, Domain.DoesNotExist, DomainAssessment.DoesNotExist) as e:
                print(f"Error processing domain {domain_key}: {e}")
                continue
        
        # Calculate final assessment based on tool type
        if tool_name == 'robins_e':
            calculate_automatic_robins_e_assessment(assessment)
        else:  # Default to RoB 2.0
            calculate_automatic_rob2_assessment(assessment)
        
        return llm_assessment
        
    except Exception as e:
        # Save error in LLM assessment record
        if llm_model:
            LLMAssessment.objects.create(
                assessment=assessment,
                llm_model=llm_model,
                prompt_used=prompt if 'prompt' in locals() else '',
                raw_response='',
                parsed_results={},
                error_message=str(e)
            )
        raise e
