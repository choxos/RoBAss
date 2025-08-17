"""
LLM Client for automated Risk of Bias assessments

This module provides interfaces to various LLM APIs for automated assessment generation.
"""

import json
import time
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from django.conf import settings
import openai
from anthropic import Anthropic
import google.generativeai as genai


class LLMClientBase(ABC):
    """Base class for LLM clients"""
    
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        self._setup_client()
    
    @abstractmethod
    def _setup_client(self):
        """Setup the API client"""
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """Generate a response from the LLM"""
        pass


class OpenAIClient(LLMClientBase):
    """Client for OpenAI/ChatGPT models"""
    
    def _setup_client(self):
        openai.api_key = self.api_key
        self.client = openai
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.1,  # Low temperature for consistent assessments
                max_tokens=4000,
                response_format={"type": "json_object"} if "gpt-" in self.model_name else None
            )
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'processing_time': processing_time,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }


class AnthropicClient(LLMClientBase):
    """Client for Anthropic/Claude models"""
    
    def _setup_client(self):
        self.client = Anthropic(api_key=self.api_key)
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=4000,
                temperature=0.1,
                system=system_prompt or "You are an expert in systematic review methodology and risk of bias assessment.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'content': response.content[0].text,
                'processing_time': processing_time,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }


class GeminiClient(LLMClientBase):
    """Client for Google Gemini models"""
    
    def _setup_client(self):
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model_name)
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=4000,
                )
            )
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'content': response.text,
                'processing_time': processing_time,
                'usage': {
                    'prompt_tokens': response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else None,
                    'completion_tokens': response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else None
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }


class LLMClientFactory:
    """Factory for creating LLM clients"""
    
    CLIENT_MAPPING = {
        'ChatGPT': OpenAIClient,
        'Claude': AnthropicClient,
        'Gemini': GeminiClient,
    }
    
    @classmethod
    def create_client(cls, provider: str, model_name: str, api_key: str) -> LLMClientBase:
        """Create an LLM client based on provider"""
        client_class = cls.CLIENT_MAPPING.get(provider)
        if not client_class:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
        return client_class(api_key, model_name)


class TextExtractor:
    """Extract text from various document formats"""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            raise ImportError("PyPDF2 is required for PDF text extraction")
        except Exception as e:
            raise Exception(f"Error extracting PDF text: {str(e)}")
    
    @staticmethod
    def extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            raise ImportError("python-docx is required for DOCX text extraction")
        except Exception as e:
            raise Exception(f"Error extracting DOCX text: {str(e)}")
    
    @staticmethod
    def extract_from_txt(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")
    
    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """Extract text based on file extension"""
        file_extension = file_path.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            return cls.extract_from_pdf(file_path)
        elif file_extension == 'docx':
            return cls.extract_from_docx(file_path)
        elif file_extension in ['txt', 'text']:
            return cls.extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")


def truncate_text(text: str, max_tokens: int = 100000) -> str:
    """
    Truncate text to fit within token limits
    Rough approximation: 1 token ≈ 4 characters for English text
    """
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    
    # Try to cut at paragraph boundaries
    paragraphs = text.split('\n\n')
    truncated = ""
    
    for paragraph in paragraphs:
        if len(truncated + paragraph) <= max_chars:
            truncated += paragraph + "\n\n"
        else:
            break
    
    if not truncated:  # If even first paragraph is too long
        truncated = text[:max_chars]
    
    return truncated.strip()


def estimate_tokens(text: str) -> int:
    """Rough estimation of token count for text"""
    # Very rough approximation - actual tokenization varies by model
    return len(text) // 4


def format_study_context(study, documents: List = None) -> str:
    """Format study information and documents for LLM prompt"""
    context = f"""
STUDY INFORMATION:
Title: {study.title}
Authors: {study.authors or 'Not provided'}
Journal: {study.journal or 'Not provided'}
Year: {study.year or 'Not provided'}
DOI: {study.doi or 'Not provided'}
Study Design: {study.study_design or 'Not provided'}
Notes: {study.notes or 'None'}

"""
    
    if documents:
        context += "STUDY DOCUMENTS:\n"
        for doc in documents:
            context += f"\n--- {doc.get_document_type_display()} ({doc.title}) ---\n"
            if doc.extracted_text:
                # Truncate each document to reasonable size
                truncated_text = truncate_text(doc.extracted_text, max_tokens=25000)
                context += truncated_text
            context += "\n\n"
    
    return context
