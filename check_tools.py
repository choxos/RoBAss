#!/usr/bin/env python
import os
import django
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robass.settings')
django.setup()

from assessments.models import AssessmentTool, Domain, SignallingQuestion

print("=== ASSESSMENT TOOLS IN DATABASE ===")
tools = AssessmentTool.objects.all()
if tools:
    for tool in tools:
        print(f"- {tool.name}: {tool.display_name} (Active: {tool.is_active})")
        domains = Domain.objects.filter(assessment_tool=tool).count()
        print(f"  Domains: {domains}")
else:
    print("No assessment tools found in database!")

print(f"\nTotal tools: {tools.count()}")
print(f"Active tools: {AssessmentTool.objects.filter(is_active=True).count()}")
