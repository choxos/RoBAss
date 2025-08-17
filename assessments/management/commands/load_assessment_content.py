import json
from django.core.management.base import BaseCommand, CommandError
from assessments.models import AssessmentTool, Domain, SignallingQuestion


TOOLS_CONTENT = {
    "rob2_parallel": {
        "domains": [
            {
                "name": "Bias arising from the randomization process",
                "short_name": "Randomization",
                "description": "Assess whether the random allocation sequence was adequately generated and concealed.",
                "order": 1,
                "questions": [
                    "Was the allocation sequence random?",
                    "Was the allocation sequence concealed until participants were enrolled and assigned?",
                    "Did baseline differences suggest a problem with the randomization process?",
                ],
            },
            {
                "name": "Bias due to deviations from intended interventions",
                "short_name": "Deviations",
                "description": "Assess whether participants and personnel were blinded and deviations affected outcomes.",
                "order": 2,
                "questions": [
                    "Were participants aware of their assigned intervention during the trial?",
                    "Were carers and people delivering the interventions aware of participants' assigned intervention?",
                    "Were there deviations from the intended intervention beyond what would be expected in usual practice?",
                    "If deviations occurred, were they likely to have affected the outcome?",
                    "If deviations occurred, were they similar between groups or were they imbalanced between groups?",
                    "Was an appropriate analysis used to estimate the effect of assignment to intervention?",
                    "If the analysis was inappropriate, was there potential for a substantial impact on the result?",
                ],
            },
            {
                "name": "Bias due to missing outcome data",
                "short_name": "Missing data",
                "description": "Assess completeness of outcome data and whether missingness could bias results.",
                "order": 3,
                "questions": [
                    "Were outcome data available for all, or nearly all, participants?",
                    "Is there evidence that the result was not biased by missing outcome data?",
                    "Could missingness in the outcome depend on its true value?",
                    "Is it likely that missingness in the outcome depended on its true value?",
                ],
            },
            {
                "name": "Bias in measurement of the outcome",
                "short_name": "Measurement",
                "description": "Assess whether outcome assessors were blinded and measurement methods were appropriate.",
                "order": 4,
                "questions": [
                    "Was the method of measuring the outcome inappropriate?",
                    "Could measurement or ascertainment of the outcome have differed between intervention groups?",
                    "Were outcome assessors aware of the intervention received?",
                    "Could assessment of the outcome have been influenced by knowledge of intervention received?",
                    "Is it likely that assessment of the outcome was influenced by knowledge of intervention received?",
                ],
            },
            {
                "name": "Bias in selection of the reported result",
                "short_name": "Reporting",
                "description": "Assess selective reporting of outcomes.",
                "order": 5,
                "questions": [
                    "Were the data that produced this result analysed in accordance with a pre-specified analysis plan?",
                    "Was the selected result likely to have been selected from multiple eligible outcome measurements?",
                    "Was the selected result likely to have been selected from multiple analyses?",
                ],
            },
        ]
    },
    # You can extend similar structured content for other tools like ROBINS-I, AMSTAR-2, etc.
}


class Command(BaseCommand):
    help = "Populate domains and signalling questions for each assessment tool."

    def handle(self, *args, **options):
        created_domains = 0
        created_questions = 0

        for tool_key, tool_data in TOOLS_CONTENT.items():
            try:
                tool = AssessmentTool.objects.get(name=tool_key)
            except AssessmentTool.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"AssessmentTool '{tool_key}' not found. Run load_assessment_tools first."))
                continue

            for domain_info in tool_data.get("domains", []):
                domain, domain_created = Domain.objects.get_or_create(
                    assessment_tool=tool,
                    name=domain_info["name"],
                    defaults={
                        "short_name": domain_info["short_name"],
                        "description": domain_info["description"],
                        "order": domain_info["order"],
                    },
                )
                if domain_created:
                    created_domains += 1

                for order, q_text in enumerate(domain_info.get("questions", []), start=1):
                    _, q_created = SignallingQuestion.objects.get_or_create(
                        domain=domain,
                        order=order,
                        defaults={"question_text": q_text},
                    )
                    if q_created:
                        created_questions += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_domains} domains and {created_questions} signalling questions."))
