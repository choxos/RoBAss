from django.core.management.base import BaseCommand
from assessments.models import LLMModel
import csv
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Load LLM models from CSV file'

    def handle(self, *args, **options):
        csv_file_path = os.path.join(settings.BASE_DIR, 'llm_models.csv')
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_file_path}')
            )
            return

        models_created = 0
        models_updated = 0

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # Skip the first line (header)
            next(file)
            reader = csv.reader(file, delimiter=',')
            
            for row in reader:
                if len(row) < 2:
                    continue
                
                # Clean up row data
                provider = row[0].strip().strip('"')
                variant = row[1].strip().strip('"')
                
                # Skip header row if it somehow wasn't skipped
                if provider == 'model' or variant == 'variant':
                    continue
                
                # Create display name
                if provider == 'ChatGPT':
                    display_name = f"OpenAI {variant}"
                elif provider == 'Claude':
                    display_name = f"Anthropic {variant}"
                elif provider == 'Gemini':
                    display_name = f"Google {variant}"
                else:
                    display_name = f"{provider} {variant}"
                
                # Set context length based on model
                context_length = 128000  # Default
                if 'gpt-5' in variant or 'o3' in variant or 'o4' in variant:
                    context_length = 200000
                elif 'gemini-2' in variant:
                    context_length = 2000000
                elif 'claude-opus-4' in variant or 'claude-sonnet-4' in variant:
                    context_length = 200000
                elif 'claude-3-5' in variant:
                    context_length = 200000
                elif 'gpt-4' in variant:
                    context_length = 128000
                
                # Create or update model
                llm_model, created = LLMModel.objects.get_or_create(
                    provider=provider,
                    model_name=variant,
                    defaults={
                        'display_name': display_name,
                        'context_length': context_length,
                        'is_active': True
                    }
                )
                
                if created:
                    models_created += 1
                    self.stdout.write(f'Created: {provider} - {variant}')
                else:
                    # Update existing model
                    llm_model.display_name = display_name
                    llm_model.context_length = context_length
                    llm_model.is_active = True
                    llm_model.save()
                    models_updated += 1
                    self.stdout.write(f'Updated: {provider} - {variant}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded LLM models. '
                f'Created: {models_created}, Updated: {models_updated}'
            )
        )
