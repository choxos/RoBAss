import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO, StringIO
import base64
import csv
from django.http import HttpResponse
from .models import Assessment, DomainAssessment, QuestionResponse


def generate_visualization(project, plot_type='traffic_light', **kwargs):
    """
    Generate risk of bias visualization plots
    
    Args:
        project: Project instance
        plot_type: Type of plot ('traffic_light', 'summary', 'weighted')
        **kwargs: Additional parameters
    
    Returns:
        base64 encoded plot image
    """
    
    # Get assessment data for the project
    assessments = Assessment.objects.filter(
        study__project=project,
        status__in=['completed', 'reviewed']
    ).prefetch_related('domain_assessments__domain')
    
    if not assessments.exists():
        return None
    
    # Prepare data
    plot_data = []
    for assessment in assessments:
        for domain_assessment in assessment.domain_assessments.all():
            if domain_assessment.bias_rating:
                plot_data.append({
                    'study': assessment.study.title[:50] + '...' if len(assessment.study.title) > 50 else assessment.study.title,
                    'domain': domain_assessment.domain.short_name,
                    'rating': domain_assessment.bias_rating,
                    'tool': assessment.assessment_tool.display_name
                })
    
    if not plot_data:
        return None
    
    df = pd.DataFrame(plot_data)
    
    # Generate plot based on type
    if plot_type == 'traffic_light':
        return _generate_traffic_light_plot(df)
    elif plot_type == 'summary':
        return _generate_summary_plot(df)
    elif plot_type == 'weighted':
        return _generate_weighted_plot(df)
    else:
        return _generate_traffic_light_plot(df)


def _generate_traffic_light_plot(df):
    """Generate traffic light plot (robvis style)"""
    
    # Set up the plot
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, max(6, len(df['study'].unique()) * 0.4)))
    
    # Define colors for bias ratings
    color_map = {
        'low': '#28a745',      # Green
        'some_concerns': '#ffc107',  # Yellow
        'high': '#dc3545',     # Red
        'no_information': '#6c757d'  # Gray
    }
    
    # Create pivot table
    pivot_df = df.pivot_table(index='study', columns='domain', values='rating', aggfunc='first')
    
    # Create the heatmap
    mask = pivot_df.isnull()
    
    # Convert ratings to numeric for plotting
    numeric_df = pivot_df.copy()
    rating_to_num = {'low': 1, 'some_concerns': 2, 'high': 3, 'no_information': 0}
    for rating, num in rating_to_num.items():
        numeric_df = numeric_df.replace(rating, num)
    
    # Create custom colormap
    colors = ['#6c757d', '#28a745', '#ffc107', '#dc3545']  # Gray, Green, Yellow, Red
    n_bins = 4
    cmap = plt.cm.colors.ListedColormap(colors)
    
    # Plot heatmap
    sns.heatmap(numeric_df, 
                annot=False,
                cmap=cmap,
                cbar=False,
                linewidths=1,
                linecolor='white',
                mask=mask,
                square=True,
                ax=ax)
    
    # Customize the plot
    ax.set_xlabel('Risk of Bias Domains', fontsize=12, fontweight='bold')
    ax.set_ylabel('Studies', fontsize=12, fontweight='bold')
    ax.set_title('Risk of Bias Assessment - Traffic Light Plot', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # Add legend
    legend_elements = [
        plt.Rectangle((0,0),1,1, facecolor='#28a745', label='Low risk'),
        plt.Rectangle((0,0),1,1, facecolor='#ffc107', label='Some concerns'),  
        plt.Rectangle((0,0),1,1, facecolor='#dc3545', label='High risk'),
        plt.Rectangle((0,0),1,1, facecolor='#6c757d', label='No information')
    ]
    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.tight_layout()
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    plot_data = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(plot_data).decode('utf-8')


def _generate_summary_plot(df):
    """Generate summary bar plot"""
    
    # Calculate proportions
    summary_data = df.groupby(['domain', 'rating']).size().unstack(fill_value=0)
    summary_props = summary_data.div(summary_data.sum(axis=1), axis=0) * 100
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Colors
    colors = {'low': '#28a745', 'some_concerns': '#ffc107', 'high': '#dc3545', 'no_information': '#6c757d'}
    
    # Create stacked bar plot
    bottom = np.zeros(len(summary_props))
    for rating in ['low', 'some_concerns', 'high', 'no_information']:
        if rating in summary_props.columns:
            ax.bar(summary_props.index, summary_props[rating], 
                   bottom=bottom, color=colors[rating], 
                   label=rating.replace('_', ' ').title())
            bottom += summary_props[rating]
    
    ax.set_xlabel('Risk of Bias Domains', fontsize=12, fontweight='bold')
    ax.set_ylabel('Percentage of Studies', fontsize=12, fontweight='bold')
    ax.set_title('Risk of Bias Assessment - Summary Plot', 
                fontsize=14, fontweight='bold')
    ax.legend()
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    plot_data = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(plot_data).decode('utf-8')


def _generate_weighted_plot(df):
    """Generate weighted bar plot"""
    
    # Weight the ratings (Low=1, Some concerns=2, High=3)
    weight_map = {'low': 1, 'some_concerns': 2, 'high': 3, 'no_information': 0}
    df['weight'] = df['rating'].map(weight_map)
    
    # Calculate weighted means
    weighted_means = df.groupby('domain')['weight'].mean().sort_values(ascending=True)
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Color gradient from green to red
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(weighted_means)))
    
    bars = ax.barh(range(len(weighted_means)), weighted_means.values, color=colors)
    
    ax.set_yticks(range(len(weighted_means)))
    ax.set_yticklabels(weighted_means.index)
    ax.set_xlabel('Average Risk Score (1=Low, 2=Some concerns, 3=High)', fontweight='bold')
    ax.set_title('Risk of Bias Assessment - Weighted Summary', fontsize=14, fontweight='bold')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 0.05, bar.get_y() + bar.get_height()/2, 
                f'{width:.2f}', ha='left', va='center')
    
    ax.set_xlim(0, 3.2)
    plt.tight_layout()
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    plot_data = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(plot_data).decode('utf-8')


def export_assessments_csv(project):
    """Export project assessments to CSV format"""
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    header = [
        'Study Title', 'Authors', 'Year', 'Journal', 'DOI', 'PMID',
        'Assessment Tool', 'Assessor', 'Status', 'Overall Bias',
        'Domain', 'Domain Rating', 'Domain Rationale', 'Last Updated'
    ]
    writer.writerow(header)
    
    # Get assessments
    assessments = Assessment.objects.filter(
        study__project=project
    ).select_related(
        'study', 'assessment_tool'
    ).prefetch_related(
        'domain_assessments__domain'
    ).order_by('study__title', 'assessment_tool__display_name')
    
    for assessment in assessments:
        base_row = [
            assessment.study.title,
            assessment.study.authors,
            assessment.study.year or '',
            assessment.study.journal,
            assessment.study.doi,
            assessment.study.pmid,
            assessment.assessment_tool.display_name,
            assessment.assessor_name,
            assessment.get_status_display(),
            assessment.overall_bias,
        ]
        
        # Add domain assessments
        domain_assessments = assessment.domain_assessments.all()
        if domain_assessments:
            for domain_assessment in domain_assessments:
                row = base_row + [
                    domain_assessment.domain.name,
                    domain_assessment.get_bias_rating_display() if domain_assessment.bias_rating else '',
                    domain_assessment.rationale,
                    assessment.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                ]
                writer.writerow(row)
        else:
            # Assessment without domain assessments
            row = base_row + ['', '', '', assessment.updated_at.strftime('%Y-%m-%d %H:%M:%S')]
            writer.writerow(row)
    
    return output.getvalue()


def export_detailed_csv(project):
    """Export detailed assessment data including signalling questions"""
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    header = [
        'Study Title', 'Authors', 'Year', 'Journal', 'Assessment Tool',
        'Domain', 'Domain Rating', 'Question Number', 'Question Text',
        'Response', 'Justification', 'Assessor', 'Date'
    ]
    writer.writerow(header)
    
    # Get assessments with questions
    assessments = Assessment.objects.filter(
        study__project=project
    ).select_related(
        'study', 'assessment_tool'
    ).prefetch_related(
        'domain_assessments__domain',
        'domain_assessments__question_responses__signalling_question'
    ).order_by('study__title')
    
    for assessment in assessments:
        for domain_assessment in assessment.domain_assessments.all():
            responses = domain_assessment.question_responses.all()
            if responses:
                for response in responses:
                    row = [
                        assessment.study.title,
                        assessment.study.authors,
                        assessment.study.year or '',
                        assessment.study.journal,
                        assessment.assessment_tool.display_name,
                        domain_assessment.domain.name,
                        domain_assessment.get_bias_rating_display() if domain_assessment.bias_rating else '',
                        response.signalling_question.order,
                        response.signalling_question.question_text,
                        response.get_response_display() if response.response else '',
                        response.justification,
                        assessment.assessor_name,
                        assessment.updated_at.strftime('%Y-%m-%d')
                    ]
                    writer.writerow(row)
            else:
                # Domain without responses
                row = [
                    assessment.study.title,
                    assessment.study.authors,
                    assessment.study.year or '',
                    assessment.study.journal,
                    assessment.assessment_tool.display_name,
                    domain_assessment.domain.name,
                    domain_assessment.get_bias_rating_display() if domain_assessment.bias_rating else '',
                    '', '', '', '', assessment.assessor_name,
                    assessment.updated_at.strftime('%Y-%m-%d')
                ]
                writer.writerow(row)
    
    return output.getvalue()
