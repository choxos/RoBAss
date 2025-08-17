from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid


class AssessmentTool(models.Model):
    """Model to represent different Risk of Bias assessment tools"""
    TOOL_CHOICES = [
        ('rob2_parallel', 'RoB 2 - Parallel Trial'),
        ('rob2_cluster', 'RoB 2 - Cluster Trial'),
        ('rob2_crossover', 'RoB 2 - Crossover Trial'),
        ('robins_i', 'ROBINS-I - Observational Studies'),
        ('robins_e', 'ROBINS-E - Observational Studies (Environmental)'),
        ('amstar2', 'AMSTAR-2 - Systematic Reviews'),
        ('robis', 'ROBIS - Systematic Reviews'),
    ]
    
    name = models.CharField(max_length=50, choices=TOOL_CHOICES, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField()
    version = models.CharField(max_length=20, default='1.0')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.display_name
    
    class Meta:
        ordering = ['display_name']


class Domain(models.Model):
    """Model to represent assessment domains for each tool"""
    assessment_tool = models.ForeignKey(AssessmentTool, on_delete=models.CASCADE, related_name='domains')
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=50)
    description = models.TextField()
    order = models.PositiveIntegerField(default=1)
    is_overall = models.BooleanField(default=False)  # For overall bias assessment
    
    def __str__(self):
        return f"{self.assessment_tool.display_name} - {self.name}"
    
    class Meta:
        ordering = ['assessment_tool', 'order']
        unique_together = ['assessment_tool', 'name']


class SignallingQuestion(models.Model):
    """Model to represent signalling questions for each domain"""
    RESPONSE_CHOICES = [
        ('yes', 'Yes'),
        ('probably_yes', 'Probably Yes'),
        ('probably_no', 'Probably No'),
        ('no', 'No'),
        ('no_information', 'No Information'),
        ('not_applicable', 'Not Applicable'),
    ]
    
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='signalling_questions')
    question_text = models.TextField()
    order = models.PositiveIntegerField(default=1)
    guidance = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.domain.short_name} - Q{self.order}"
    
    class Meta:
        ordering = ['domain', 'order']
        unique_together = ['domain', 'order']


class Project(models.Model):
    """Model to represent a research project/study collection"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Null for guest users
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)  # For guest users
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-updated_at']


class Study(models.Model):
    """Model to represent individual studies being assessed"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='studies')
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True)
    journal = models.CharField(max_length=200, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True, 
                                     validators=[MinValueValidator(1900), MaxValueValidator(2100)])
    doi = models.CharField(max_length=100, blank=True)
    pmid = models.CharField(max_length=20, blank=True)
    study_design = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title[:100]
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['project', 'title']


class Assessment(models.Model):
    """Model to represent a complete RoB assessment for a study"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed'),
    ]
    
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name='assessments')
    assessment_tool = models.ForeignKey(AssessmentTool, on_delete=models.CASCADE)
    assessor_name = models.CharField(max_length=100, blank=True)
    assessor_email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    overall_bias = models.CharField(max_length=50, blank=True)  # Low, Some concerns, High
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.study.title[:50]} - {self.assessment_tool.display_name}"
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['study', 'assessment_tool']


class DomainAssessment(models.Model):
    """Model to represent assessment for each domain"""
    BIAS_CHOICES = [
        ('low', 'Low risk'),
        ('some_concerns', 'Some concerns'),
        ('high', 'High risk'),
        ('no_information', 'No information'),
    ]
    
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='domain_assessments')
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    bias_rating = models.CharField(max_length=20, choices=BIAS_CHOICES, blank=True)
    rationale = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.assessment} - {self.domain.short_name}"
    
    class Meta:
        unique_together = ['assessment', 'domain']


class QuestionResponse(models.Model):
    """Model to represent responses to signalling questions"""
    RESPONSE_CHOICES = [
        ('yes', 'Yes'),
        ('probably_yes', 'Probably Yes'),
        ('probably_no', 'Probably No'),
        ('no', 'No'),
        ('no_information', 'No Information'),
        ('not_applicable', 'Not Applicable'),
    ]
    
    domain_assessment = models.ForeignKey(DomainAssessment, on_delete=models.CASCADE, related_name='question_responses')
    signalling_question = models.ForeignKey(SignallingQuestion, on_delete=models.CASCADE)
    response = models.CharField(max_length=20, choices=RESPONSE_CHOICES, blank=True)
    justification = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.domain_assessment} - Q{self.signalling_question.order}"
    
    class Meta:
        unique_together = ['domain_assessment', 'signalling_question']


class AssessmentExport(models.Model):
    """Model to track exported assessments"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='exports')
    export_type = models.CharField(max_length=20, choices=[('csv', 'CSV'), ('plot', 'Plot')])
    file_path = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.project.name} - {self.export_type} export"
    
    class Meta:
        ordering = ['-created_at']


class StudyDocument(models.Model):
    """Documents uploaded for a study (full text, protocol, etc.)"""
    DOCUMENT_TYPES = [
        ('full_text', 'Full Text Article'),
        ('protocol', 'Study Protocol'),
        ('supplementary', 'Supplementary Material'),
        ('registry', 'Trial Registry Entry'),
        ('other', 'Other Document'),
    ]
    
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='study_documents/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveIntegerField(help_text='Size in bytes')
    extracted_text = models.TextField(blank=True, help_text='Extracted text content for LLM processing')
    
    def __str__(self):
        return f"{self.study.title[:50]} - {self.get_document_type_display()}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class LLMModel(models.Model):
    """Available LLM models for automated assessments"""
    provider = models.CharField(max_length=50)  # e.g., 'Gemini', 'Claude', 'ChatGPT'
    model_name = models.CharField(max_length=100)  # e.g., 'gemini-2.5-pro'
    display_name = models.CharField(max_length=150)  # Human-readable name
    is_active = models.BooleanField(default=True)
    context_length = models.PositiveIntegerField(default=128000, help_text='Context window size in tokens')
    api_endpoint = models.URLField(blank=True, help_text='Custom API endpoint if needed')
    
    class Meta:
        unique_together = ('provider', 'model_name')
        ordering = ['provider', 'display_name']
    
    def __str__(self):
        return f"{self.provider} - {self.display_name}"


class LLMAssessment(models.Model):
    """LLM-generated assessment results"""
    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE, related_name='llm_assessment')
    llm_model = models.ForeignKey(LLMModel, on_delete=models.CASCADE)
    prompt_used = models.TextField()
    raw_response = models.TextField()
    parsed_results = models.JSONField()  # Structured assessment results
    confidence_score = models.FloatField(null=True, blank=True, help_text='LLM confidence in assessment (0-1)')
    created_at = models.DateTimeField(auto_now_add=True)
    processing_time = models.FloatField(null=True, blank=True, help_text='Processing time in seconds')
    error_message = models.TextField(blank=True, help_text='Error details if processing failed')
    
    def __str__(self):
        return f"LLM Assessment for {self.assessment} using {self.llm_model}"
