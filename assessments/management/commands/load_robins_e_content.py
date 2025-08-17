from django.core.management.base import BaseCommand
from assessments.models import AssessmentTool, Domain, SignallingQuestion


class Command(BaseCommand):
    """
    Populate ROBINS-E tool with comprehensive domains and signalling questions.

    Run with:
        python manage.py load_robins_e_content
    """

    def handle(self, *args, **options):
        try:
            robins_e_tool = AssessmentTool.objects.get(name='robins_e')
        except AssessmentTool.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('ROBINS-E tool not found. Please run load_assessment_tools first.')
            )
            return

        # Clear existing domains for clean slate
        robins_e_tool.domains.all().delete()

        domains_data = [
            {
                "name": "Risk of bias due to confounding",
                "short_name": "Confounding",
                "description": "Baseline differences between intervention groups that affect the outcome",
                "order": 1,
                "questions": [
                    {
                        "text": "Was the analysis method for the main exposure appropriate?",
                        "order": 1,
                        "guidance": "Consider whether the analysis method is appropriate for estimating the effect of the main exposure on the outcome. This includes consideration of study design, confounding control methods, and statistical approach.",
                        "explanation": "This question assesses whether the statistical analysis method used is suitable for the study design and research question. The analysis should appropriately account for the observational nature of the study and potential confounders."
                    },
                    {
                        "text": "Were the important confounding factors identified and controlled for?",
                        "order": 2,
                        "guidance": "Consider whether all important confounding factors that could affect both the exposure and outcome have been identified and appropriately controlled for in the analysis.",
                        "explanation": "Important confounders are factors that are associated with both the exposure and the outcome, and their absence from the analysis could bias the results. This includes both measured and unmeasured confounders."
                    },
                    {
                        "text": "Were confounding factors measured validly and reliably?",
                        "order": 3,
                        "guidance": "Consider the quality of measurement for confounding factors included in the analysis. Poor measurement can lead to residual confounding even when factors are included in the model.",
                        "explanation": "Even when confounders are identified and included in the analysis, poor measurement quality can lead to inadequate control of confounding. Valid and reliable measurement is crucial for effective confounder control."
                    },
                    {
                        "text": "Were any variables that were measured after the start of exposure controlled for?",
                        "order": 4,
                        "guidance": "Consider whether the analysis inappropriately controlled for variables that were measured or occurred after the exposure began, as these may be on the causal pathway (over-adjustment bias).",
                        "explanation": "Controlling for post-exposure variables can introduce over-adjustment bias by blocking the causal pathway from exposure to outcome. Only pre-exposure confounders should typically be controlled for."
                    },
                    {
                        "text": "Do negative controls or other approaches suggest serious uncontrolled confounding?",
                        "order": 5,
                        "guidance": "Consider whether negative control analyses, sensitivity analyses, or other approaches suggest that important confounding remains uncontrolled despite the analysis methods used.",
                        "explanation": "Negative controls and other sensitivity analyses can provide evidence about the extent of residual confounding. These approaches help assess whether uncontrolled confounding might explain the observed associations."
                    }
                ]
            },
            {
                "name": "Risk of bias in measurement of exposures",
                "short_name": "Exposure Measurement",
                "description": "Bias arising from measurement or classification of exposures",
                "order": 2,
                "questions": [
                    {
                        "text": "Could the exposure have been measured differently between groups being compared?",
                        "order": 1,
                        "guidance": "Consider whether systematic differences in exposure measurement between comparison groups could have occurred.",
                        "explanation": "Differential exposure measurement between groups can bias effect estimates. This includes differences in measurement methods, timing, or quality between exposed and unexposed groups."
                    },
                    {
                        "text": "Were outcome assessors aware of the exposure status of study participants?",
                        "order": 2,
                        "guidance": "Consider whether those measuring or classifying exposures knew about participants' outcome status, which could bias exposure assessment.",
                        "explanation": "Knowledge of outcome status during exposure assessment can lead to biased exposure classification, particularly for subjective or retrospectively assessed exposures."
                    },
                    {
                        "text": "Could misclassification of exposure status have affected results?",
                        "order": 3,
                        "guidance": "Consider whether errors in exposure classification could be substantial enough to bias the results, particularly if misclassification is differential between groups.",
                        "explanation": "Both differential and non-differential misclassification can bias results, but differential misclassification is typically more problematic as it can bias results away from or toward the null."
                    }
                ]
            },
            {
                "name": "Risk of bias in selection of participants into the study",
                "short_name": "Selection",
                "description": "Bias arising from selection of participants based on characteristics observed after the start of exposure",
                "order": 3,
                "questions": [
                    {
                        "text": "Was selection of participants into the study related to the exposure and likely influenced by the outcome or a cause of the outcome?",
                        "order": 1,
                        "guidance": "Consider whether the selection process for study participants was related to both exposure and outcome status in a way that could bias results.",
                        "explanation": "Selection bias occurs when the association between exposure and outcome differs between those selected for the study and the target population, often due to selection based on factors related to both exposure and outcome."
                    },
                    {
                        "text": "Were the methods of outcome assessment comparable between exposed and unexposed groups?",
                        "order": 2,
                        "guidance": "Consider whether systematic differences in how outcomes were assessed between exposure groups could have occurred.",
                        "explanation": "Differential outcome assessment methods between exposure groups can introduce bias. Assessment methods should be comparable to ensure fair comparison between groups."
                    },
                    {
                        "text": "Was follow-up time likely to be sufficient for outcomes to occur?",
                        "order": 3,
                        "guidance": "Consider whether the duration of follow-up was adequate to observe outcomes of interest, and whether follow-up duration differed between exposure groups.",
                        "explanation": "Insufficient or differential follow-up time between exposure groups can bias results by not allowing adequate time for outcomes to develop or by differential loss to follow-up."
                    }
                ]
            },
            {
                "name": "Risk of bias due to post-exposure interventions",
                "short_name": "Post-exposure Interventions",
                "description": "Bias arising from interventions or treatments applied after the start of exposure",
                "order": 4,
                "questions": [
                    {
                        "text": "Were post-exposure variables that could be affected by the exposure controlled for?",
                        "order": 1,
                        "guidance": "Consider whether the analysis inappropriately controlled for variables that could be affected by the exposure, potentially blocking the causal pathway.",
                        "explanation": "Controlling for post-exposure variables that are affected by the exposure can introduce over-adjustment bias by blocking part of the causal effect of the exposure on the outcome."
                    },
                    {
                        "text": "Were there important differences in ancillary treatments between exposure groups?",
                        "order": 2,
                        "guidance": "Consider whether differences in treatments, interventions, or care received after exposure onset could have affected outcomes differentially between groups.",
                        "explanation": "Differential ancillary treatments or interventions between exposure groups after exposure onset can confound the relationship between the main exposure and outcome."
                    },
                    {
                        "text": "Could differences in ancillary treatments have affected the outcome?",
                        "order": 3,
                        "guidance": "Assess whether any identified differences in post-exposure treatments or interventions could have meaningfully influenced the study outcomes.",
                        "explanation": "Even if differential treatments exist, they only pose a bias risk if they could plausibly affect the outcome of interest. The magnitude and direction of potential effects should be considered."
                    }
                ]
            },
            {
                "name": "Risk of bias due to missing data",
                "short_name": "Missing Data",
                "description": "Bias arising from missing outcome, exposure or confounder data",
                "order": 5,
                "questions": [
                    {
                        "text": "Were outcome data reasonably complete for all participants?",
                        "order": 1,
                        "guidance": "Consider the proportion of participants with missing outcome data and whether this could introduce bias.",
                        "explanation": "Missing outcome data can bias results, particularly if missingness is related to both exposure and outcome. The amount and pattern of missing data should be evaluated."
                    },
                    {
                        "text": "Were participants excluded due to missing data on exposure status?",
                        "order": 2,
                        "guidance": "Consider whether exclusion of participants with missing exposure data could have introduced selection bias.",
                        "explanation": "Excluding participants with missing exposure data can introduce selection bias if the reasons for missing exposure data are related to the outcome or other study variables."
                    },
                    {
                        "text": "Were participants excluded due to missing data on important confounders?",
                        "order": 3,
                        "guidance": "Assess whether exclusions based on missing confounder data could have biased the results.",
                        "explanation": "Complete-case analysis excluding participants with missing confounder data can introduce bias if missingness is associated with exposure, outcome, or other variables."
                    },
                    {
                        "text": "Was the analysis method appropriate for handling missing data?",
                        "order": 4,
                        "guidance": "Consider whether the statistical methods used to handle missing data were appropriate and unlikely to introduce bias.",
                        "explanation": "Different methods for handling missing data have different assumptions and limitations. The chosen method should be appropriate for the pattern and mechanism of missing data."
                    }
                ]
            },
            {
                "name": "Risk of bias in measurement of outcomes",
                "short_name": "Outcome Measurement",
                "description": "Bias arising from measurement or ascertainment of outcomes",
                "order": 6,
                "questions": [
                    {
                        "text": "Could the outcome measure have been influenced by knowledge of the exposure received?",
                        "order": 1,
                        "guidance": "Consider whether knowledge of exposure status could have influenced outcome measurement or assessment, particularly for subjective outcomes.",
                        "explanation": "Detection bias can occur when outcome assessors' knowledge of exposure status influences their assessment, particularly for subjective or investigator-assessed outcomes."
                    },
                    {
                        "text": "Were outcome assessors blinded to exposure status?",
                        "order": 2,
                        "guidance": "Assess whether outcome assessors were unaware of participants' exposure status during outcome assessment.",
                        "explanation": "Blinding of outcome assessors helps prevent detection bias. When blinding is not possible, objective outcome measures may be less susceptible to bias than subjective measures."
                    },
                    {
                        "text": "Were the methods of outcome assessment comparable between groups?",
                        "order": 3,
                        "guidance": "Consider whether outcome assessment methods were consistent and comparable between different exposure groups.",
                        "explanation": "Systematic differences in outcome assessment methods between exposure groups can introduce bias. Methods should be standardized and applied consistently across all study participants."
                    },
                    {
                        "text": "Could differences in outcome assessment have affected results?",
                        "order": 4,
                        "guidance": "Evaluate whether any identified differences in outcome assessment could have meaningfully biased the study results.",
                        "explanation": "The potential impact of assessment differences depends on the nature of the outcome, the extent of differences, and their likely direction and magnitude of effect on results."
                    }
                ]
            },
            {
                "name": "Risk of bias in selection of the reported result",
                "short_name": "Reported Results",
                "description": "Bias arising from selection of results for presentation based on the findings",
                "order": 7,
                "questions": [
                    {
                        "text": "Were the data analyses in accordance with a pre-specified plan?",
                        "order": 1,
                        "guidance": "Consider whether the reported analyses were planned in advance and whether deviations from the plan were appropriately justified.",
                        "explanation": "Pre-specification of analysis plans helps prevent selective reporting and data-driven analysis choices that can bias results. Post-hoc analyses should be clearly identified."
                    },
                    {
                        "text": "Were there multiple outcome measurements or analysis methods from which results could be chosen?",
                        "order": 2,
                        "guidance": "Assess whether multiple ways of measuring outcomes or conducting analyses were available, creating opportunities for selective reporting.",
                        "explanation": "When multiple outcome measures, time points, or analysis methods are available, there's potential for selective reporting of the most favorable results, which can bias findings."
                    },
                    {
                        "text": "Was the study free from selective reporting of results based on the findings?",
                        "order": 3,
                        "guidance": "Consider whether there's evidence of selective reporting, such as emphasis on statistically significant results or omission of pre-planned analyses.",
                        "explanation": "Selective reporting based on results (e.g., emphasizing significant findings while downplaying non-significant ones) can give a biased impression of the evidence."
                    }
                ]
            },
            {
                "name": "Overall risk of bias",
                "short_name": "Overall",
                "description": "Overall judgment about the risk of bias for the study result",
                "order": 8,
                "is_overall": True,
                "questions": []
            }
        ]

        for domain_data in domains_data:
            # Create domain
            domain = Domain.objects.create(
                assessment_tool=robins_e_tool,
                name=domain_data["name"],
                short_name=domain_data["short_name"],
                description=domain_data["description"],
                order=domain_data["order"],
                is_overall=domain_data.get("is_overall", False)
            )

            self.stdout.write(f"Created domain: {domain.name}")

            # Create signalling questions
            for question_data in domain_data["questions"]:
                question = SignallingQuestion.objects.create(
                    domain=domain,
                    question_text=question_data["text"],
                    order=question_data["order"],
                    guidance=question_data["guidance"],
                    explanation=question_data["explanation"],
                    is_required=True
                )
                self.stdout.write(f"  • Added question {question.order}: {question_data['text'][:50]}...")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully populated ROBINS-E tool with {len(domains_data)} domains')
        )
