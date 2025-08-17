"""
Enhanced Views for PDF Upload and LLM Assessment Workflow

This module contains views for the enhanced workflow:
1. PDF upload and metadata extraction
2. Study creation with auto-populated metadata
3. LLM-assisted assessment
4. Results review and manual editing
"""

import json
import os
import tempfile
from typing import Dict, Any

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from .models import (
    AssessmentTool, Project, Study, Assessment, StudyDocument, 
    LLMModel, LLMAssessment, DomainAssessment, QuestionResponse
)
from .forms_enhanced import (
    DocumentUploadForm, StudyCreationForm, AssessmentMethodForm,
    MetadataReviewForm, LLMConfigurationForm
)
from .services.pdf_service import extract_pdf_content
from .services.metadata_service import extract_metadata_from_identifier
from .services.llm_prompts import RoB2PromptTemplates
from .services.llm_service import LLMClient
from .rob2_engine import calculate_rob2_assessment


@login_required
def enhanced_study_create_view(request, project_id, tool_name):
    """Enhanced study creation with PDF upload and metadata extraction"""
    project = get_object_or_404(Project, id=project_id, user=request.user)
    tool = get_object_or_404(AssessmentTool, name=tool_name, is_active=True)
    
    if request.method == 'POST':
        upload_form = DocumentUploadForm(request.POST, request.FILES)
        
        if upload_form.is_valid():
            # Process uploaded PDF and/or metadata identifier
            pdf_file = upload_form.cleaned_data.get('pdf_file')
            identifier = upload_form.cleaned_data.get('identifier')
            
            # Store processing results in session for next step
            processing_results = {}
            
            # Process PDF if uploaded
            if pdf_file:
                try:
                    # Save PDF temporarily
                    temp_path = default_storage.save(
                        f'temp_pdfs/{pdf_file.name}',
                        ContentFile(pdf_file.read())
                    )
                    full_path = os.path.join(settings.MEDIA_ROOT, temp_path)
                    
                    # Extract PDF content
                    pdf_results = extract_pdf_content(full_path)
                    processing_results['pdf_results'] = pdf_results
                    
                    # Clean up temp file
                    default_storage.delete(temp_path)
                    
                    if pdf_results['success']:
                        messages.success(
                            request, 
                            f"PDF processed successfully. Extracted {pdf_results['word_count']} words."
                        )
                    else:
                        messages.warning(
                            request, 
                            f"PDF processing had issues: {pdf_results.get('error', 'Unknown error')}"
                        )
                        
                except Exception as e:
                    messages.error(request, f"PDF processing failed: {str(e)}")
            
            # Process metadata identifier if provided
            if identifier:
                try:
                    metadata_results = extract_metadata_from_identifier(identifier)
                    processing_results['metadata_results'] = metadata_results
                    
                    if 'error' not in metadata_results:
                        messages.success(request, "Metadata extracted successfully from identifier.")
                    else:
                        messages.warning(
                            request, 
                            f"Metadata extraction failed: {metadata_results['error']}"
                        )
                        
                except Exception as e:
                    messages.error(request, f"Metadata extraction failed: {str(e)}")
            
            # Store results in session
            request.session['processing_results'] = processing_results
            request.session['project_id'] = str(project.id)
            request.session['tool_name'] = tool_name
            
            return redirect('assessments:metadata_review')
    
    else:
        upload_form = DocumentUploadForm()
    
    context = {
        'upload_form': upload_form,
        'project': project,
        'tool': tool,
        'title': f'Add Study to {project.name} - {tool.display_name}'
    }
    return render(request, 'assessments/enhanced_study_create.html', context)


@login_required
def metadata_review_view(request):
    """Review extracted metadata and PDF content before creating study"""
    processing_results = request.session.get('processing_results')
    if not processing_results:
        messages.error(request, "No processing results found. Please start over.")
        return redirect('assessments:project_list')
    
    project_id = request.session.get('project_id')
    tool_name = request.session.get('tool_name')
    
    if not project_id or not tool_name:
        messages.error(request, "Session data incomplete. Please start over.")
        return redirect('assessments:project_list')
    
    project = get_object_or_404(Project, id=project_id, user=request.user)
    tool = get_object_or_404(AssessmentTool, name=tool_name, is_active=True)
    
    # Merge PDF and metadata results
    combined_metadata = {}
    pdf_results = processing_results.get('pdf_results', {})
    metadata_results = processing_results.get('metadata_results', {})
    
    # Priority: metadata from identifier > PDF metadata
    if pdf_results.get('success'):
        combined_metadata.update(pdf_results.get('metadata', {}))
    
    if metadata_results and 'error' not in metadata_results:
        combined_metadata.update(metadata_results)
    
    # Add extraction info
    combined_metadata['word_count'] = pdf_results.get('word_count', 0)
    combined_metadata['extraction_success'] = pdf_results.get('success', False)
    
    if request.method == 'POST':
        review_form = MetadataReviewForm(request.POST)
        study_form = StudyCreationForm(request.POST)
        
        if review_form.is_valid() and study_form.is_valid():
            # Create study with confirmed metadata
            study = study_form.save(commit=False)
            study.project = project
            study.save()
            
            # Save extracted text and content if available
            if pdf_results.get('success'):
                # Create StudyDocument for the PDF content
                doc = StudyDocument.objects.create(
                    study=study,
                    document_type='full_text',
                    title=f"Full Text - {study.title[:50]}",
                    file_size=len(pdf_results.get('text', '').encode('utf-8')),
                    extracted_text=pdf_results.get('text', '')
                )
                
                # Store rob_content in session for assessment
                request.session['rob_content'] = pdf_results.get('rob_content', {})
                request.session['study_id'] = study.id
            
            messages.success(request, f'Study "{study.title}" created successfully!')
            
            # Redirect to assessment method selection
            return redirect('assessments:assessment_method_selection')
    
    else:
        # Pre-populate forms with extracted data
        review_form = MetadataReviewForm(initial=combined_metadata)
        study_form = StudyCreationForm(initial=combined_metadata)
    
    context = {
        'review_form': review_form,
        'study_form': study_form,
        'project': project,
        'tool': tool,
        'pdf_results': pdf_results,
        'metadata_results': metadata_results,
        'combined_metadata': combined_metadata,
        'title': 'Review Extracted Metadata'
    }
    return render(request, 'assessments/metadata_review.html', context)


@login_required
def assessment_method_selection_view(request):
    """Select assessment method (manual vs LLM)"""
    study_id = request.session.get('study_id')
    tool_name = request.session.get('tool_name')
    
    if not study_id or not tool_name:
        messages.error(request, "Session data incomplete. Please start over.")
        return redirect('assessments:project_list')
    
    study = get_object_or_404(Study, id=study_id, project__user=request.user)
    tool = get_object_or_404(AssessmentTool, name=tool_name, is_active=True)
    
    if request.method == 'POST':
        form = AssessmentMethodForm(request.POST)
        
        if form.is_valid():
            assessment_method = form.cleaned_data['assessment_method']
            
            # Create assessment
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
            
            if assessment_method == 'manual':
                messages.success(request, 'Assessment created. You can now perform manual assessment.')
                return redirect('assessments:assessment_detail', assessment_id=assessment.id)
            
            elif assessment_method in ['llm', 'both']:
                llm_model = form.cleaned_data['llm_model']
                api_key = form.cleaned_data.get('api_key', '')
                
                # Store LLM configuration in session
                request.session['llm_config'] = {
                    'model_id': llm_model.id,
                    'api_key': api_key,
                    'assessment_method': assessment_method
                }
                request.session['assessment_id'] = assessment.id
                
                if api_key:
                    return redirect('assessments:llm_assessment_run')
                else:
                    return redirect('assessments:llm_configuration')
    
    else:
        form = AssessmentMethodForm()
    
    context = {
        'form': form,
        'study': study,
        'tool': tool,
        'title': 'Choose Assessment Method'
    }
    return render(request, 'assessments/assessment_method_selection.html', context)


@login_required
def llm_configuration_view(request):
    """Configure LLM settings before running assessment"""
    llm_config = request.session.get('llm_config')
    if not llm_config:
        messages.error(request, "No LLM configuration found. Please start over.")
        return redirect('assessments:project_list')
    
    llm_model = get_object_or_404(LLMModel, id=llm_config['model_id'])
    
    if request.method == 'POST':
        form = LLMConfigurationForm(request.POST)
        
        if form.is_valid():
            # Update session with configuration
            llm_config.update({
                'api_key': form.cleaned_data['api_key'],
                'temperature': form.cleaned_data['temperature'],
                'use_extracted_content': form.cleaned_data['use_extracted_content']
            })
            request.session['llm_config'] = llm_config
            
            return redirect('assessments:llm_assessment_run')
    
    else:
        form = LLMConfigurationForm(initial={
            'llm_model': llm_model,
            'api_key': llm_config.get('api_key', ''),
            'temperature': 0.1,
            'use_extracted_content': True
        })
    
    context = {
        'form': form,
        'llm_model': llm_model,
        'title': 'Configure LLM Settings'
    }
    return render(request, 'assessments/llm_configuration.html', context)


@login_required
def llm_assessment_run_view(request):
    """Run LLM assessment"""
    assessment_id = request.session.get('assessment_id')
    llm_config = request.session.get('llm_config')
    rob_content = request.session.get('rob_content', {})
    
    if not assessment_id or not llm_config:
        messages.error(request, "Session data incomplete. Please start over.")
        return redirect('assessments:project_list')
    
    assessment = get_object_or_404(
        Assessment, 
        id=assessment_id, 
        study__project__user=request.user
    )
    
    if request.method == 'POST':
        try:
            # Get the study document with extracted text
            study_doc = StudyDocument.objects.filter(
                study=assessment.study,
                document_type='full_text'
            ).first()
            
            if not study_doc or not study_doc.extracted_text:
                messages.error(request, "No extracted text found for assessment.")
                return redirect('assessments:assessment_detail', assessment_id=assessment.id)
            
            # Initialize LLM client
            llm_model = LLMModel.objects.get(id=llm_config['model_id'])
            llm_client = LLMClient(
                provider=llm_model.provider,
                model_name=llm_model.model_name,
                api_key=llm_config['api_key']
            )
            
            # Generate prompt
            prompt_templates = RoB2PromptTemplates()
            
            if llm_config.get('use_extracted_content', True) and rob_content:
                prompt = prompt_templates.generate_quick_assessment_prompt(
                    study_doc.extracted_text,
                    rob_content
                )
            else:
                prompt = prompt_templates.generate_assessment_prompt(
                    study_doc.extracted_text
                )
            
            # Run LLM assessment
            response = llm_client.generate_assessment(
                prompt=prompt,
                temperature=llm_config.get('temperature', 0.1)
            )
            
            if response['success']:
                # Parse LLM response
                llm_responses = response['assessment_data']
                
                # Save LLM assessment record
                llm_assessment = LLMAssessment.objects.create(
                    assessment=assessment,
                    llm_model=llm_model,
                    prompt_used=prompt[:5000],  # Truncate for storage
                    raw_response=response['raw_response'][:10000],
                    parsed_results=llm_responses,
                    confidence_score=response.get('confidence', 0.8),
                    processing_time=response.get('processing_time', 0)
                )
                
                # Convert LLM responses to assessment format and save
                response_mapping = {
                    'Yes': 'yes', 'Y': 'yes',
                    'Probably Yes': 'probably_yes', 'PY': 'probably_yes',
                    'Probably No': 'probably_no', 'PN': 'probably_no',
                    'No': 'no', 'N': 'no',
                    'No Information': 'no_information', 'NI': 'no_information'
                }
                
                # Save responses to database
                for domain_key, domain_responses in llm_responses.items():
                    domain_num = int(domain_key.split('_')[1])
                    domain = assessment.assessment_tool.domains.get(order=domain_num)
                    domain_assessment = assessment.domain_assessments.get(domain=domain)
                    
                    for question_key, question_data in domain_responses.items():
                        question_num = int(question_key.split('.')[1])
                        signalling_question = domain.signalling_questions.get(order=question_num)
                        
                        # Map LLM response to our format
                        llm_answer = question_data.get('answer', '')
                        mapped_response = response_mapping.get(llm_answer, 'no_information')
                        
                        # Create or update question response
                        QuestionResponse.objects.update_or_create(
                            domain_assessment=domain_assessment,
                            signalling_question=signalling_question,
                            defaults={
                                'response': mapped_response,
                                'justification': question_data.get('justification', '')
                            }
                        )
                
                # Calculate domain and overall assessments
                try:
                    rob_results = calculate_automatic_rob2_assessment(assessment)
                    if rob_results:
                        messages.success(
                            request, 
                            "LLM assessment completed successfully with automatic RoB calculation!"
                        )
                    else:
                        messages.success(
                            request,
                            "LLM assessment completed successfully!"
                        )
                except Exception as e:
                    messages.warning(
                        request,
                        f"LLM assessment completed, but automatic calculation failed: {str(e)}"
                    )
                
                # Clean up session data
                for key in ['assessment_id', 'llm_config', 'rob_content', 'study_id', 'processing_results']:
                    request.session.pop(key, None)
                
                # Redirect based on assessment method
                if llm_config.get('assessment_method') == 'both':
                    messages.info(
                        request,
                        "LLM assessment complete. You can now review and edit the responses manually."
                    )
                
                return redirect('assessments:assessment_detail', assessment_id=assessment.id)
            
            else:
                messages.error(
                    request,
                    f"LLM assessment failed: {response.get('error', 'Unknown error')}"
                )
                return redirect('assessments:assessment_detail', assessment_id=assessment.id)
                
        except Exception as e:
            messages.error(request, f"Assessment failed: {str(e)}")
            return redirect('assessments:assessment_detail', assessment_id=assessment.id)
    
    # GET request - show assessment progress page
    llm_model = LLMModel.objects.get(id=llm_config['model_id'])
    
    context = {
        'assessment': assessment,
        'llm_model': llm_model,
        'llm_config': llm_config,
        'has_extracted_content': bool(rob_content),
        'title': 'Run LLM Assessment'
    }
    return render(request, 'assessments/llm_assessment_run.html', context)


def calculate_automatic_rob2_assessment(assessment):
    """Calculate automatic RoB 2.0 assessment from user responses (imported from views.py)"""
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
