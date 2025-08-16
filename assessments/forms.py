from django import forms
from .models import Project, Study, Assessment, DomainAssessment, QuestionResponse, AssessmentTool


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects"""
    
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your project, research question, or methodology'
            })
        }
        help_texts = {
            'name': 'A descriptive name for your assessment project',
            'description': 'Optional: Provide context about your systematic review or research project'
        }


class StudyForm(forms.ModelForm):
    """Form for adding studies to projects"""
    
    class Meta:
        model = Study
        fields = ['title', 'authors', 'journal', 'year', 'doi', 'pmid', 'study_design', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full title of the study',
                'required': True
            }),
            'authors': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Author names (e.g., Smith J, Johnson A, Brown B)'
            }),
            'journal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Journal name'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Publication year (YYYY)',
                'min': 1900,
                'max': 2100
            }),
            'doi': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10.1000/xyz123'
            }),
            'pmid': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PubMed ID'
            }),
            'study_design': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Randomized controlled trial, Cohort study'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes or comments about this study'
            })
        }
        help_texts = {
            'title': 'The complete title of the study as published',
            'authors': 'List of study authors',
            'year': 'Year of publication',
            'doi': 'Digital Object Identifier (if available)',
            'pmid': 'PubMed identifier (if available)',
            'study_design': 'Type of study design',
            'notes': 'Any additional information about the study'
        }
    
    def clean_year(self):
        """Validate publication year"""
        year = self.cleaned_data.get('year')
        if year:
            current_year = 2024  # You might want to use datetime.now().year
            if year < 1900 or year > current_year + 1:
                raise forms.ValidationError(f'Year must be between 1900 and {current_year + 1}')
        return year
    
    def clean_doi(self):
        """Basic DOI validation"""
        doi = self.cleaned_data.get('doi')
        if doi:
            doi = doi.strip()
            if doi and not doi.startswith('10.'):
                raise forms.ValidationError('DOI should start with "10."')
        return doi


class AssessmentForm(forms.ModelForm):
    """Form for assessment metadata"""
    
    class Meta:
        model = Assessment
        fields = ['assessor_name', 'assessor_email', 'notes']
        widgets = {
            'assessor_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name'
            }),
            'assessor_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'General notes about this assessment'
            })
        }


class DomainAssessmentForm(forms.ModelForm):
    """Form for domain-level bias assessment"""
    
    class Meta:
        model = DomainAssessment
        fields = ['bias_rating', 'rationale']
        widgets = {
            'bias_rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'rationale': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Provide rationale for this domain rating based on the signalling questions'
            })
        }


class QuestionResponseForm(forms.ModelForm):
    """Form for individual signalling question responses"""
    
    class Meta:
        model = QuestionResponse
        fields = ['response', 'justification']
        widgets = {
            'response': forms.Select(attrs={
                'class': 'form-select response-select'
            }),
            'justification': forms.Textarea(attrs={
                'class': 'form-control justification-textarea',
                'rows': 3,
                'placeholder': 'Provide justification for your response...'
            })
        }
        help_texts = {
            'justification': 'Explain the reasoning behind your response with reference to specific information from the study'
        }


class BulkStudyImportForm(forms.Form):
    """Form for importing multiple studies at once"""
    
    CSV_HELP_TEXT = """
    Upload a CSV file with the following columns:
    title, authors, journal, year, doi, pmid, study_design, notes
    
    Only the 'title' column is required. Other columns are optional.
    """
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text=CSV_HELP_TEXT
    )
    
    def clean_csv_file(self):
        """Validate CSV file"""
        file = self.cleaned_data.get('csv_file')
        if file:
            if not file.name.endswith('.csv'):
                raise forms.ValidationError('File must be a CSV file')
            
            # Check file size (limit to 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size cannot exceed 5MB')
        
        return file


class AssessmentSearchForm(forms.Form):
    """Form for searching and filtering assessments"""
    
    # We'll populate these dynamically in the form __init__ method
    TOOL_CHOICES = [('', 'All Tools')]
    STATUS_CHOICES = [('', 'All Statuses'), ('draft', 'Draft'), ('completed', 'Completed'), ('reviewed', 'Reviewed')]
    
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search studies, projects, or assessors...'
        })
    )
    
    tool = forms.ChoiceField(
        choices=TOOL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Filter assessments created after this date'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Filter assessments created before this date'
    )
