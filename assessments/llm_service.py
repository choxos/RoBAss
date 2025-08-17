"""
LLM Assessment Service for automated Risk of Bias evaluations

This module orchestrates the complete LLM assessment process including
text extraction, prompt generation, LLM interaction, and result parsing.
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from django.utils import timezone

from .models import Assessment, StudyDocument, LLMModel, LLMAssessment
from .llm_client import LLMClientFactory, TextExtractor, format_study_context, truncate_text
from .llm_prompts import ROB2_SYSTEM_PROMPT, ROB2_ASSESSMENT_PROMPT, get_validation_prompt
from .rob2_engine import calculate_rob2_assessment


class LLMAssessmentService:
    """Service for conducting automated LLM-based RoB assessments"""
    
    def __init__(self, api_key: str, llm_model: LLMModel):
        self.api_key = api_key
        self.llm_model = llm_model
        self.client = LLMClientFactory.create_client(
            llm_model.provider, 
            llm_model.model_name, 
            api_key
        )
    
    def conduct_assessment(self, assessment: Assessment, 
                         documents: List[StudyDocument] = None) -> Dict[str, Any]:
        """
        Conduct a complete LLM assessment for a study
        
        Args:
            assessment: The Assessment object to evaluate
            documents: List of uploaded documents to analyze
            
        Returns:
            Dict containing assessment results and metadata
        """
        start_time = time.time()
        
        try:
            # Extract text from documents if not already done
            self._ensure_text_extracted(documents or [])
            
            # Prepare study context
            study_context = format_study_context(
                assessment.study, 
                documents or list(assessment.study.documents.all())
            )
            
            # Truncate context if needed to fit within model limits
            study_context = self._prepare_context_for_model(study_context)
            
            # Generate the full assessment prompt
            assessment_prompt = ROB2_ASSESSMENT_PROMPT.format(
                study_context=study_context
            )
            
            # Get LLM response
            response = self.client.generate_response(
                prompt=assessment_prompt,
                system_prompt=ROB2_SYSTEM_PROMPT
            )
            
            processing_time = time.time() - start_time
            
            if not response['success']:
                return {
                    'success': False,
                    'error': response.get('error', 'Unknown error'),
                    'processing_time': processing_time
                }
            
            # Parse and validate the response
            parsed_results = self._parse_llm_response(response['content'])
            
            if not parsed_results:
                return {
                    'success': False,
                    'error': 'Failed to parse LLM response into valid format',
                    'processing_time': processing_time,
                    'raw_response': response['content']
                }
            
            # Validate assessment logic using our RoB2 engine
            validation_results = self._validate_assessment_logic(parsed_results)
            
            # Save LLM assessment results
            llm_assessment = self._save_llm_assessment(
                assessment=assessment,
                prompt_used=assessment_prompt,
                raw_response=response['content'],
                parsed_results=parsed_results,
                processing_time=processing_time,
                validation_results=validation_results
            )
            
            return {
                'success': True,
                'llm_assessment_id': llm_assessment.id,
                'parsed_results': parsed_results,
                'validation_results': validation_results,
                'processing_time': processing_time,
                'usage_stats': response.get('usage', {})
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _ensure_text_extracted(self, documents: List[StudyDocument]) -> None:
        """Extract text from documents that don't have it yet"""
        for doc in documents:
            if not doc.extracted_text and doc.file:
                try:
                    doc.extracted_text = TextExtractor.extract_text(doc.file.path)
                    doc.save()
                except Exception as e:
                    # Log error but continue with other documents
                    print(f"Failed to extract text from {doc.file.name}: {str(e)}")
    
    def _prepare_context_for_model(self, study_context: str) -> str:
        """Prepare study context to fit within model token limits"""
        # Reserve tokens for prompt template and response
        reserved_tokens = 8000
        available_tokens = self.llm_model.context_length - reserved_tokens
        
        return truncate_text(study_context, max_tokens=available_tokens)
    
    def _parse_llm_response(self, raw_response: str) -> Optional[Dict[str, Any]]:
        """Parse and validate LLM response JSON"""
        try:
            # Try to extract JSON from response
            response_text = raw_response.strip()
            
            # Handle case where response is wrapped in markdown code blocks
            if response_text.startswith('```json'):
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                response_text = response_text[start:end]
            elif response_text.startswith('```'):
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                response_text = response_text[start:end]
            
            parsed = json.loads(response_text)
            
            # Validate required structure
            required_domains = ['domain_1', 'domain_2', 'domain_3', 'domain_4', 'domain_5', 'overall']
            if all(domain in parsed for domain in required_domains):
                return parsed
            else:
                print(f"Missing required domains in response: {set(required_domains) - set(parsed.keys())}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error parsing LLM response: {str(e)}")
            return None
    
    def _validate_assessment_logic(self, parsed_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate assessment logic against RoB2 engine"""
        validation = {'warnings': [], 'errors': [], 'suggestions': []}
        
        try:
            # Extract question responses for validation
            responses = {}
            
            for domain_num in range(1, 6):
                domain_key = f'domain_{domain_num}'
                if domain_key in parsed_results:
                    domain_data = parsed_results[domain_key]
                    if 'questions' in domain_data:
                        for q_key, q_data in domain_data['questions'].items():
                            if 'response' in q_data:
                                # Map responses to our engine format
                                response = q_data['response'].upper()
                                if response == 'PROBABLY_YES':
                                    response = 'PY'
                                elif response == 'PROBABLY_NO':
                                    response = 'PN'
                                elif response == 'NO_INFORMATION':
                                    response = 'NI'
                                elif response == 'NOT_APPLICABLE':
                                    response = 'NA'
                                elif response == 'YES':
                                    response = 'Y'
                                elif response == 'NO':
                                    response = 'N'
                                
                                responses[q_key] = response
            
            # Run our validation engine
            if len(responses) >= 22:  # Minimum questions for RoB2
                engine_results = calculate_rob2_assessment(responses)
                
                # Compare LLM results with engine results
                for domain_num in range(1, 6):
                    domain_key = f'domain_{domain_num}'
                    if domain_key in engine_results and domain_key in parsed_results:
                        llm_risk = parsed_results[domain_key].get('risk_assessment', '').lower()
                        engine_risk = engine_results[domain_key]['risk'].lower()
                        
                        if llm_risk != engine_risk:
                            validation['warnings'].append(
                                f"Domain {domain_num} risk mismatch: LLM={llm_risk}, Engine={engine_risk}"
                            )
                
                # Check overall assessment
                if 'overall' in engine_results and 'overall' in parsed_results:
                    llm_overall = parsed_results['overall'].get('risk_assessment', '').lower()
                    engine_overall = engine_results['overall']['risk'].lower()
                    
                    if llm_overall != engine_overall:
                        validation['errors'].append(
                            f"Overall risk mismatch: LLM={llm_overall}, Engine={engine_overall}"
                        )
            
        except Exception as e:
            validation['errors'].append(f"Validation error: {str(e)}")
        
        return validation
    
    def _save_llm_assessment(self, assessment: Assessment, prompt_used: str, 
                           raw_response: str, parsed_results: Dict[str, Any],
                           processing_time: float, validation_results: Dict[str, Any]) -> LLMAssessment:
        """Save LLM assessment results to database"""
        
        # Calculate confidence score from individual domain confidences
        confidence_scores = []
        for domain_num in range(1, 6):
            domain_key = f'domain_{domain_num}'
            if domain_key in parsed_results:
                domain_confidence = parsed_results[domain_key].get('confidence', 0.5)
                confidence_scores.append(domain_confidence)
        
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        # Add validation results to parsed results
        parsed_results['validation'] = validation_results
        
        llm_assessment, created = LLMAssessment.objects.update_or_create(
            assessment=assessment,
            defaults={
                'llm_model': self.llm_model,
                'prompt_used': prompt_used,
                'raw_response': raw_response,
                'parsed_results': parsed_results,
                'confidence_score': overall_confidence,
                'processing_time': processing_time,
                'error_message': ''
            }
        )
        
        return llm_assessment
    
    def refine_assessment(self, llm_assessment: LLMAssessment) -> Dict[str, Any]:
        """Refine an existing assessment by running validation prompts"""
        try:
            validation_prompt = get_validation_prompt(
                json.dumps(llm_assessment.parsed_results, indent=2)
            )
            
            response = self.client.generate_response(
                prompt=validation_prompt,
                system_prompt=ROB2_SYSTEM_PROMPT
            )
            
            if response['success']:
                refined_results = self._parse_llm_response(response['content'])
                if refined_results:
                    # Update the assessment with refined results
                    llm_assessment.parsed_results = refined_results
                    llm_assessment.save()
                    
                    return {
                        'success': True,
                        'refined_results': refined_results
                    }
            
            return {
                'success': False,
                'error': 'Failed to refine assessment'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def estimate_assessment_cost(documents: List[StudyDocument], llm_model: LLMModel) -> Dict[str, Any]:
    """Estimate the cost and token usage for an LLM assessment"""
    total_text = ""
    for doc in documents:
        if doc.extracted_text:
            total_text += doc.extracted_text
    
    # Rough token estimation
    estimated_input_tokens = len(total_text) // 4 + 3000  # Base prompt tokens
    estimated_output_tokens = 4000  # Expected response length
    total_tokens = estimated_input_tokens + estimated_output_tokens
    
    # Very rough cost estimation (varies greatly by provider)
    cost_per_1k_tokens = {
        'ChatGPT': 0.03,  # GPT-4 approximate
        'Claude': 0.08,   # Claude-3 approximate  
        'Gemini': 0.01    # Gemini Pro approximate
    }
    
    estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens.get(llm_model.provider, 0.05)
    
    return {
        'estimated_input_tokens': estimated_input_tokens,
        'estimated_output_tokens': estimated_output_tokens,
        'total_tokens': total_tokens,
        'estimated_cost_usd': round(estimated_cost, 2),
        'fits_in_context': total_tokens <= llm_model.context_length
    }
