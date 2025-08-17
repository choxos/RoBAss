"""
Enhanced Forms for PDF Upload and Study Creation Workflow

This module contains forms for the new workflow:
1. PDF upload with metadata extraction
2. Study creation with auto-populated fields
3. Assessment method selection (manual vs LLM)
"""

from django import forms
from django.core.validators import FileExtensionValidator
from .models import Study, StudyDocument, LLMModel, Assessment
import re


class DocumentUploadForm(forms.Form):
    """Form for uploading PDF and providing PMID/DOI"""
    
    # File upload
    pdf_file = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf',
            'id': 'pdf-upload'
        }),
        help_text="Upload the full-text PDF of the research article"
    )
    
    # Metadata identifier
    identifier = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter PMID, DOI, or article URL',
            'id': 'metadata-identifier'
        }),
        help_text="Provide PMID (e.g., 12345678), DOI (e.g., 10.1000/xyz123), or article URL for automatic metadata extraction"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        pdf_file = cleaned_data.get('pdf_file')
        identifier = cleaned_data.get('identifier')
        
        if not pdf_file and not identifier:
            raise forms.ValidationError(
                "Please provide either a PDF file or a PMID/DOI/URL for metadata extraction."
            )
        
        return cleaned_data
    
    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file:
            # Check file size (limit to 50MB)
            if pdf_file.size > 50 * 1024 * 1024:
                raise forms.ValidationError("PDF file size cannot exceed 50MB")
            
            # Basic PDF validation
            if not pdf_file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("File must be a PDF")
                
        return pdf_file
    
    def clean_identifier(self):
        identifier = self.cleaned_data.get('identifier')
        if identifier:
            identifier = identifier.strip()
            
            # Basic validation for common identifier patterns
            if not (
                re.match(r'^\d+$', identifier) or  # PMID
                re.match(r'^10\.\d+/', identifier) or  # DOI
                identifier.startswith('doi:') or
                identifier.startswith('http')  # URL
            ):
                # Allow through anyway - the metadata service will handle validation
                pass
                
        return identifier


class StudyCreationForm(forms.ModelForm):
    """Enhanced form for study creation with metadata integration"""
    
    class Meta:
        model = Study
        fields = ['title', 'authors', 'journal', 'year', 'doi', 'pmid', 'study_design', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Study title (auto-populated from metadata)',
                'required': True
            }),
            'authors': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Author names (auto-populated from metadata)'
            }),
            'journal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Journal name (auto-populated from metadata)'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Publication year (auto-populated)',
                'min': 1900,
                'max': 2100
            }),
            'doi': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10.1000/xyz123 (auto-populated)'
            }),
            'pmid': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PubMed ID (auto-populated)'
            }),
            'study_design': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Randomized controlled trial'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about this study'
            })
        }
        help_texts = {
            'title': 'The study title will be auto-populated from metadata if available',
            'authors': 'Author list will be auto-populated from metadata if available',
            'year': 'Publication year will be auto-populated from metadata',
            'doi': 'DOI will be auto-populated if found in metadata',
            'pmid': 'PMID will be auto-populated if found in metadata',
            'study_design': 'Specify the type of study design',
            'notes': 'Any additional information about the study'
        }


class AssessmentMethodForm(forms.Form):
    """Form for choosing assessment method (manual vs LLM)"""
    
    ASSESSMENT_CHOICES = [
        ('manual', 'Manual Assessment'),
        ('llm', 'LLM-Assisted Assessment'),
        ('both', 'Both (LLM first, then manual review)')
    ]
    
    assessment_method = forms.ChoiceField(
        choices=ASSESSMENT_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial='manual',
        help_text="Choose how you want to conduct the Risk of Bias assessment"
    )
    
    # LLM selection (shown only when LLM is chosen)
    llm_model = forms.ModelChoiceField(
        queryset=LLMModel.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'llm-model-select'
        }),
        help_text="Select the LLM model for assessment"
    )
    
    # API key for LLM (optional - can be provided later)
    api_key = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your API key (optional - can be provided later)',
            'id': 'api-key-input'
        }),
        help_text="Provide your API key for the selected LLM service (can be entered later if needed)"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        assessment_method = cleaned_data.get('assessment_method')
        llm_model = cleaned_data.get('llm_model')
        
        if assessment_method in ['llm', 'both'] and not llm_model:
            raise forms.ValidationError(
                "Please select an LLM model for LLM-assisted assessment."
            )
        
        return cleaned_data


class LLMConfigurationForm(forms.Form):
    """Form for configuring LLM settings"""
    
    llm_model = forms.ModelChoiceField(
        queryset=LLMModel.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text="Select the LLM model for assessment"
    )
    
    api_key = forms.CharField(
        max_length=500,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your API key for the selected LLM service'
        }),
        help_text="Your API key will be used securely and not stored permanently"
    )
    
    temperature = forms.FloatField(
        initial=0.1,
        min_value=0.0,
        max_value=1.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0',
            'max': '1'
        }),
        help_text="Lower values (0.1) for more consistent, conservative assessments"
    )
    
    use_extracted_content = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Use programmatically extracted relevant content to improve assessment efficiency"
    )


class StudyDocumentForm(forms.ModelForm):
    """Form for uploading additional study documents"""
    
    class Meta:
        model = StudyDocument
        fields = ['document_type', 'title', 'file']
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document title or description'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt'
            })
        }
        help_texts = {
            'document_type': 'Select the type of document you are uploading',
            'title': 'Provide a descriptive title for this document',
            'file': 'Supported formats: PDF, Word documents, text files'
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (limit to 25MB)
            if file.size > 25 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 25MB")
            
            # Check file extension
            allowed_extensions = ['pdf', 'doc', 'docx', 'txt']
            file_extension = file.name.lower().split('.')[-1]
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
                )
                
        return file


class MetadataReviewForm(forms.Form):
    """Form for reviewing and confirming extracted metadata"""
    
    title = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        }),
        help_text="Extracted study title"
    )
    
    authors = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        }),
        help_text="Extracted author information"
    )
    
    journal = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        }),
        help_text="Extracted journal information"
    )
    
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        }),
        help_text="Extracted publication year"
    )
    
    doi = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        }),
        help_text="Extracted DOI"
    )
    
    pmid = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        }),
        help_text="Extracted PMID"
    )
    
    abstract = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'readonly': 'readonly'
        }),
        help_text="Extracted abstract"
    )
    
    word_count = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        }),
        help_text="Word count of extracted text"
    )
    
    extraction_success = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'disabled': 'disabled'
        }),
        help_text="Whether text extraction was successful"
    )
    
    # Confirmation checkboxes
    metadata_confirmed = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Confirm that the extracted metadata is correct"
    )
    
    text_quality_confirmed = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Confirm that the extracted text quality is sufficient for assessment"
    )


class AssessmentReviewForm(forms.Form):
    """Form for reviewing LLM assessment results before saving"""
    
    confidence_threshold = forms.FloatField(
        initial=0.7,
        min_value=0.0,
        max_value=1.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0',
            'max': '1'
        }),
        help_text="Minimum confidence level for accepting LLM responses automatically"
    )
    
    review_low_confidence = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Flag responses below confidence threshold for manual review"
    )
    
    save_llm_responses = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Save LLM responses as the initial assessment (can be edited later)"
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notes about the LLM assessment quality or any concerns'
        }),
        help_text="Optional notes about the assessment"
    )
