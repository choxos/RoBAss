from django.core.management.base import BaseCommand
from assessments.models import AssessmentTool, Domain


class Command(BaseCommand):
    """
    Populate the database with the core Risk-of-Bias assessment tools and minimal placeholder domains.

    Run with:
        python manage.py load_assessment_tools
    """

    def handle(self, *args, **options):
        tools_data = [
            {
                "name": "rob2_parallel",
                "display_name": "RoB 2 – Parallel Trial",
                "description": "Risk of bias 2.0 tool for randomised parallel-group trials.",
            },
            {
                "name": "rob2_cluster",
                "display_name": "RoB 2 – Cluster Trial",
                "description": "Risk of bias 2.0 tool for cluster-randomised trials.",
            },
            {
                "name": "rob2_crossover",
                "display_name": "RoB 2 – Crossover Trial",
                "description": "Risk of bias 2.0 tool for randomised crossover trials.",
            },
            {
                "name": "robins_i",
                "display_name": "ROBINS-I – Observational Studies (Intervention)",
                "description": "Risk of bias in non-randomised studies of interventions.",
            },
            {
                "name": "robins_e",
                "display_name": "ROBINS-E – Observational Studies (Exposure)",
                "description": "Risk of bias in non-randomised studies of environmental exposures.",
            },
            {
                "name": "amstar2",
                "display_name": "AMSTAR-2 – Systematic Reviews",
                "description": "Assessing the methodological quality of systematic reviews.",
            },
            {
                "name": "robis",
                "display_name": "ROBIS – Systematic Reviews",
                "description": "Risk of bias in systematic reviews.",
            },
        ]

        for tool in tools_data:
            obj, created = AssessmentTool.objects.update_or_create(
                name=tool["name"],
                defaults={
                    "display_name": tool["display_name"],
                    "description": tool["description"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created {obj.display_name}"))
            else:
                self.stdout.write(f"Updated {obj.display_name}")

            # ensure at least one placeholder domain so that downstream logic works
            if not obj.domains.exists():
                Domain.objects.create(
                    assessment_tool=obj,
                    name="Overall",
                    short_name="Overall",
                    description="Overall risk of bias domain placeholder.",
                    order=1,
                    is_overall=True,
                )
                self.stdout.write("  • added placeholder domain")

        self.stdout.write(self.style.SUCCESS("Assessment tools population complete."))
