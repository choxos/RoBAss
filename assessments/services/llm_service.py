"""
LLM Service for Risk of Bias Assessment

This service provides a unified interface for different LLM providers
to conduct Risk of Bias assessments.
"""

import json
import time
import logging
import re
from typing import Dict, Any, Optional
from ..models import LLMModel

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified client for different LLM providers"""
    
    def __init__(self, provider: str, model_name: str, api_key: str):
        self.provider = provider.lower()
        self.model_name = model_name
        self.api_key = api_key
        
        # Initialize provider-specific client
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        try:
            if self.provider == 'openai' or self.provider == 'chatgpt':
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                
            elif self.provider == 'anthropic' or self.provider == 'claude':
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                
            elif self.provider == 'google' or self.provider == 'gemini':
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
                
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                
        except ImportError as e:
            logger.error(f"Required library not installed for {self.provider}: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} client: {str(e)}")
    
    def generate_assessment(self, prompt: str, temperature: float = 0.1) -> Dict[str, Any]:
        """Generate assessment using the configured LLM"""
        start_time = time.time()
        
        try:
            if not self.client:
                return {
                    'success': False,
                    'error': f'LLM client not initialized for {self.provider}'
                }
            
            # Generate response based on provider
            if self.provider in ['openai', 'chatgpt']:
                response = self._generate_openai(prompt, temperature)
            elif self.provider in ['anthropic', 'claude']:
                response = self._generate_anthropic(prompt, temperature)
            elif self.provider in ['google', 'gemini']:
                response = self._generate_google(prompt, temperature)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported provider: {self.provider}'
                }
            
            processing_time = time.time() - start_time
            
            if response['success']:
                # Try to parse JSON response
                try:
                    assessment_data = json.loads(response['content'])
                    return {
                        'success': True,
                        'raw_response': response['content'],
                        'assessment_data': assessment_data,
                        'processing_time': processing_time,
                        'confidence': self._estimate_confidence(assessment_data)
                    }
                except json.JSONDecodeError:
                    # Try to extract JSON from response
                    extracted_json = self._extract_json_from_response(response['content'])
                    if extracted_json:
                        return {
                            'success': True,
                            'raw_response': response['content'],
                            'assessment_data': extracted_json,
                            'processing_time': processing_time,
                            'confidence': self._estimate_confidence(extracted_json)
                        }
                    else:
                        return {
                            'success': False,
                            'error': 'Failed to parse LLM response as JSON',
                            'raw_response': response['content']
                        }
            else:
                return response
                
        except Exception as e:
            return {
                'success': False,
                'error': f'LLM generation failed: {str(e)}',
                'processing_time': time.time() - start_time
            }
    
    def _generate_openai(self, prompt: str, temperature: float) -> Dict[str, Any]:
        """Generate response using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=4000
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'OpenAI API error: {str(e)}'
            }
    
    def _generate_anthropic(self, prompt: str, temperature: float) -> Dict[str, Any]:
        """Generate response using Anthropic API"""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=4000,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                'success': True,
                'content': response.content[0].text
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Anthropic API error: {str(e)}'
            }
    
    def _generate_google(self, prompt: str, temperature: float) -> Dict[str, Any]:
        """Generate response using Google Generative AI"""
        try:
            # Configure generation parameters
            generation_config = {
                'temperature': temperature,
                'max_output_tokens': 4000,
            }
            
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return {
                'success': True,
                'content': response.text
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Google API error: {str(e)}'
            }
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict]:
        """Try to extract JSON from response text"""
        import re
        
        # Look for JSON blocks
        json_patterns = [
            r'```json\n(.*?)\n```',
            r'```\n(.*?)\n```',
            r'\{.*\}',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _estimate_confidence(self, assessment_data: Dict) -> float:
        """Estimate confidence score based on response completeness"""
        try:
            total_questions = 0
            answered_questions = 0
            
            for domain_key, domain_responses in assessment_data.items():
                if not domain_key.startswith('domain_'):
                    continue
                    
                for question_key, question_data in domain_responses.items():
                    total_questions += 1
                    if isinstance(question_data, dict):
                        answer = question_data.get('answer', '')
                        justification = question_data.get('justification', '')
                        
                        if answer and answer != 'No Information' and len(justification) > 10:
                            answered_questions += 1
            
            if total_questions == 0:
                return 0.0
            
            return answered_questions / total_questions
            
        except Exception:
            return 0.5  # Default confidence


class LLMService:
    """Service class for risk of bias assessment using LLMs"""
    
    def __init__(self, llm_model: LLMModel):
        self.llm_model = llm_model
        self.client = LLMClient(
            provider=llm_model.provider,
            model_name=llm_model.model_name,
            api_key=llm_model.api_key
        )
    
    def generate_assessment(self, prompt: str) -> str:
        """Generate assessment using the configured LLM and return raw response"""
        response = self.client.generate_assessment(prompt, temperature=0.1)
        
        if response['success']:
            return response['raw_response']
        else:
            raise Exception(f"LLM generation failed: {response.get('error', 'Unknown error')}")
    
    def parse_rob2_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response for RoB 2.0 assessment"""
        try:
            # Try to extract JSON from response
            extracted_json = self._extract_json_from_response(llm_response)
            if extracted_json:
                return {
                    'domains': extracted_json,
                    'confidence': self._estimate_confidence(extracted_json)
                }
            else:
                # Fallback: try to parse structured text response
                return self._parse_structured_rob2_response(llm_response)
                
        except Exception as e:
            logger.error(f"Error parsing RoB 2.0 response: {str(e)}")
            return {'domains': {}, 'confidence': 0.0}
    
    def parse_robins_e_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response for ROBINS-E assessment"""
        try:
            # Try to extract JSON from response
            extracted_json = self._extract_json_from_response(llm_response)
            if extracted_json:
                return {
                    'domains': extracted_json,
                    'confidence': self._estimate_confidence(extracted_json)
                }
            else:
                # Fallback: try to parse structured text response
                return self._parse_structured_robins_e_response(llm_response)
                
        except Exception as e:
            logger.error(f"Error parsing ROBINS-E response: {str(e)}")
            return {'domains': {}, 'confidence': 0.0}
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict]:
        """Try to extract JSON from response text"""
        # Look for JSON blocks
        json_patterns = [
            r'```json\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```',
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    # Clean up the match
                    clean_match = match.strip()
                    if clean_match.startswith('{') and clean_match.endswith('}'):
                        return json.loads(clean_match)
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _parse_structured_rob2_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured text response for RoB 2.0"""
        domains = {}
        
        # Try to find domain sections
        domain_patterns = {
            'domain_1': r'Domain\s*1[:\s]*.*?(?=Domain\s*2|$)',
            'domain_2': r'Domain\s*2[:\s]*.*?(?=Domain\s*3|$)', 
            'domain_3': r'Domain\s*3[:\s]*.*?(?=Domain\s*4|$)',
            'domain_4': r'Domain\s*4[:\s]*.*?(?=Domain\s*5|$)',
            'domain_5': r'Domain\s*5[:\s]*.*?(?=$)'
        }
        
        response_mapping = {
            'yes': 'Y', 'y': 'Y',
            'probably yes': 'PY', 'py': 'PY',
            'probably no': 'PN', 'pn': 'PN', 
            'no': 'N', 'n': 'N',
            'no information': 'NI', 'ni': 'NI'
        }
        
        for domain_key, pattern in domain_patterns.items():
            domain_text = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if domain_text:
                domain_content = domain_text.group(0)
                domains[domain_key] = self._extract_questions_from_domain_text(domain_content, response_mapping)
        
        return {
            'domains': domains,
            'confidence': self._estimate_confidence(domains)
        }
    
    def _parse_structured_robins_e_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured text response for ROBINS-E"""
        domains = {}
        
        # ROBINS-E has 7 domains
        domain_patterns = {
            'domain_1': r'Domain\s*1[:\s]*.*?(?=Domain\s*2|$)',
            'domain_2': r'Domain\s*2[:\s]*.*?(?=Domain\s*3|$)', 
            'domain_3': r'Domain\s*3[:\s]*.*?(?=Domain\s*4|$)',
            'domain_4': r'Domain\s*4[:\s]*.*?(?=Domain\s*5|$)',
            'domain_5': r'Domain\s*5[:\s]*.*?(?=Domain\s*6|$)',
            'domain_6': r'Domain\s*6[:\s]*.*?(?=Domain\s*7|$)',
            'domain_7': r'Domain\s*7[:\s]*.*?(?=$)'
        }
        
        response_mapping = {
            'yes': 'Y', 'y': 'Y',
            'probably yes': 'PY', 'py': 'PY',
            'probably no': 'PN', 'pn': 'PN', 
            'no': 'N', 'n': 'N',
            'no information': 'NI', 'ni': 'NI'
        }
        
        for domain_key, pattern in domain_patterns.items():
            domain_text = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if domain_text:
                domain_content = domain_text.group(0)
                domains[domain_key] = self._extract_questions_from_domain_text(domain_content, response_mapping)
        
        return {
            'domains': domains,
            'confidence': self._estimate_confidence(domains)
        }
    
    def _extract_questions_from_domain_text(self, domain_text: str, response_mapping: Dict[str, str]) -> Dict[str, Dict]:
        """Extract question responses from domain text"""
        questions = {}
        
        # Look for question patterns like "1.1", "2.3", etc.
        question_patterns = re.findall(r'(\d+\.\d+)\s*[:\-]?\s*(.*?)(?=\d+\.\d+|$)', domain_text, re.DOTALL)
        
        for question_id, question_content in question_patterns:
            # Extract answer from content
            answer = 'NI'  # Default
            justification = question_content.strip()
            
            # Look for explicit answers
            for response_text, mapped_value in response_mapping.items():
                if re.search(rf'\b{re.escape(response_text)}\b', question_content, re.IGNORECASE):
                    answer = mapped_value
                    break
            
            questions[question_id] = {
                'response': answer,
                'justification': justification[:500]  # Limit length
            }
        
        return questions
    
    def _estimate_confidence(self, domains: Dict) -> float:
        """Estimate confidence based on response quality"""
        total_questions = 0
        answered_questions = 0
        
        for domain_key, domain_data in domains.items():
            if not isinstance(domain_data, dict):
                continue
                
            for q_key, q_data in domain_data.items():
                if isinstance(q_data, dict):
                    total_questions += 1
                    response = q_data.get('response', 'NI')
                    justification = q_data.get('justification', '')
                    
                    if response != 'NI' and len(justification.strip()) > 20:
                        answered_questions += 1
        
        if total_questions == 0:
            return 0.0
        
        return answered_questions / total_questions


def test_llm_connection(provider: str, model_name: str, api_key: str) -> Dict[str, Any]:
    """Test LLM connection and functionality"""
    try:
        client = LLMClient(provider, model_name, api_key)
        
        test_prompt = """You are testing the connection. Please respond with exactly this JSON:
        {
            "test": "success",
            "provider": "your_provider_name",
            "status": "working"
        }"""
        
        response = client.generate_assessment(test_prompt, temperature=0.1)
        
        if response['success']:
            return {
                'success': True,
                'message': 'LLM connection test successful',
                'response_preview': response['raw_response'][:200] + "..." if len(response['raw_response']) > 200 else response['raw_response']
            }
        else:
            return {
                'success': False,
                'error': response.get('error', 'Unknown error'),
                'message': 'LLM connection test failed'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'LLM connection test failed'
        }
