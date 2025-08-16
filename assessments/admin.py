from django.contrib import admin
from .models import (
    AssessmentTool, Domain, SignallingQuestion, Project, Study, 
    Assessment, DomainAssessment, QuestionResponse, AssessmentExport
)


@admin.register(AssessmentTool)
class AssessmentToolAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'version', 'is_active', 'created_at']
    list_filter = ['is_active', 'name']
    search_fields = ['display_name', 'description']
    ordering = ['display_name']


class SignallingQuestionInline(admin.TabularInline):
    model = SignallingQuestion
    extra = 0
    ordering = ['order']


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['name', 'assessment_tool', 'short_name', 'order', 'is_overall']
    list_filter = ['assessment_tool', 'is_overall']
    search_fields = ['name', 'short_name', 'description']
    ordering = ['assessment_tool', 'order']
    inlines = [SignallingQuestionInline]


@admin.register(SignallingQuestion)
class SignallingQuestionAdmin(admin.ModelAdmin):
    list_display = ['domain', 'order', 'question_text', 'is_required']
    list_filter = ['domain__assessment_tool', 'is_required']
    search_fields = ['question_text', 'guidance']
    ordering = ['domain', 'order']


class StudyInline(admin.TabularInline):
    model = Study
    extra = 0
    fields = ['title', 'authors', 'year']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'description']
    ordering = ['-updated_at']
    inlines = [StudyInline]
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'authors', 'year', 'journal']
    list_filter = ['year', 'project', 'created_at']
    search_fields = ['title', 'authors', 'journal', 'doi']
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['study', 'assessment_tool', 'assessor_name', 'status', 'overall_bias', 'updated_at']
    list_filter = ['assessment_tool', 'status', 'overall_bias', 'created_at']
    search_fields = ['study__title', 'assessor_name', 'assessor_email']
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DomainAssessment)
class DomainAssessmentAdmin(admin.ModelAdmin):
    list_display = ['assessment', 'domain', 'bias_rating']
    list_filter = ['domain__assessment_tool', 'bias_rating', 'domain']
    search_fields = ['assessment__study__title', 'domain__name']
    ordering = ['assessment', 'domain__order']


@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ['domain_assessment', 'signalling_question', 'response']
    list_filter = ['response', 'signalling_question__domain__assessment_tool']
    search_fields = ['domain_assessment__assessment__study__title']
    ordering = ['domain_assessment', 'signalling_question__order']


@admin.register(AssessmentExport)
class AssessmentExportAdmin(admin.ModelAdmin):
    list_display = ['project', 'export_type', 'created_at']
    list_filter = ['export_type', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
