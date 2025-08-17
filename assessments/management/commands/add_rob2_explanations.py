from django.core.management.base import BaseCommand
from assessments.models import AssessmentTool, Domain, SignallingQuestion

class Command(BaseCommand):
    help = 'Add explanations to RoB 2.0 signalling questions from the crib sheet'

    def handle(self, *args, **options):
        # RoB 2.0 explanations from the crib sheet
        rob2_explanations = {
            # Domain 1: Randomization process
            ('1', '1'): """Consider the methods used to generate the allocation sequence and whether the allocation sequence was adequately concealed from those involved in enrolling and assigning participants. The concern is whether the allocation sequence could be predicted because the methods used were non-random or the allocation sequence was not adequately concealed.""",
            
            ('1', '2'): """Information about how the randomization sequence was concealed should be sought in the study protocol, the study report, or in correspondence with the study authors. Allocation concealment is distinct from blinding. Allocation concealment seeks to prevent selection bias and confounding, while blinding seeks to prevent performance and detection bias.""",
            
            ('1', '3'): """A baseline imbalance in a prognostic factor may suggest a problem with the randomization process. Review key prognostic factors (those related to the outcome) to judge whether important imbalances exist and whether they are likely to be due to chance or to problems with the randomization process.""",

            # Domain 2: Deviations from intended interventions
            ('2', '1'): """Consider all persons involved in implementing the intervention being studied, including the trial participants (who may be aware of their intervention assignment due to obvious differences between intervention and comparator).""",
            
            ('2', '2'): """Consider all persons involved in caring for participants, such as doctors, nurses and other healthcare providers, who might be aware of the intervention assignment.""",
            
            ('2', '3'): """Consider whether there were systematic differences in how the experimental intervention and control were given, or in the care provided in addition to the interventions being compared.""",
            
            ('2', '4'): """Consider whether departures from the intended intervention that arose during the study could have meaningfully impacted the outcome. Consider the nature of the outcome and the nature of the departures.""",
            
            ('2', '5'): """Consider whether any systematic departures from the intended intervention that could have affected the outcome were balanced between groups.""",
            
            ('2', '6'): """Consider whether the analysis was appropriate for addressing the research question and whether it correctly analysed participants in the groups to which they were randomized (intention-to-treat principle).""",
            
            ('2', '7'): """Consider the potential impact on the results of the failure to analyse participants in the group to which they were randomized. If there was non-adherence to the intended intervention but participants were correctly analysed according to their randomized groups, answer N or PN.""",

            # Domain 3: Missing outcome data
            ('3', '1'): """Consider whether outcome data were available for all, or nearly all, randomized participants. The important issue is how much outcome data for the specific result being assessed are missing.""",
            
            ('3', '2'): """Appropriate analyses include: complete-case analysis with examination of prognostic factors; use of imputation methods based on pre-specified analysis; analysis methods (e.g. mixed models for repeated measures) that account for the probability of missing data.""",
            
            ('3', '3'): """The informative missingness relates to the outcome being measured. For subjective outcomes, data are more likely to be missing informatively than for objective outcomes. For example, participants experiencing an adverse drug reaction may withdraw from the study, leading to missing data on the primary efficacy outcome.""",
            
            ('3', '4'): """Consider whether missingness in the outcome is likely to depend on its true value. For example, participants with poor outcomes may be more likely to miss follow-up visits.""",

            # Domain 4: Measurement of the outcome
            ('4', '1'): """Consider whether the method of outcome assessment was inappropriate (e.g. the measurement method had poor validity or reliability, or was not properly calibrated).""",
            
            ('4', '2'): """Consider whether outcome assessors used different methods for assessing the outcome in different intervention groups, or whether outcome assessments were made at different times or with different frequency in different groups.""",
            
            ('4', '3'): """Consider whether the outcome assessors knew which intervention each study participant received. This includes patient self-reported outcomes if patients were not blinded to the intervention assignment.""",
            
            ('4', '4'): """Consider whether it is likely that assessment of the outcome could be influenced by knowledge of the intervention received. This is more likely for subjective outcomes and less likely for objective outcomes (e.g. all-cause mortality).""",
            
            ('4', '5'): """Consider whether it is plausible that the outcome assessment was influenced by knowledge of the intervention received by the study participants.""",

            # Domain 5: Selection of the reported result
            ('5', '1'): """A pre-specified analysis plan that is finalized before unblinded outcome data are available for analysis should be sought. The analysis plan may be found in a study protocol, a statistical analysis plan, a registry entry, or other documentation.""",
            
            ('5', '2'): """Consider whether the study authors selected the reported result from multiple eligible outcome measurements (e.g. multiple measurement instruments, multiple time points, multiple analyses) within the outcome domain on the basis of the results.""",
            
            ('5', '3'): """Consider whether the study authors selected the reported result from multiple eligible analyses (e.g. unadjusted and adjusted; final values and change scores; with and without transformation; with and without adjustment for multiple testing) of the outcome measurement on the basis of the results.""",
        }
        
        try:
            # Get RoB 2.0 parallel trial tool
            tool = AssessmentTool.objects.get(name='rob2_parallel')
            
            updated_count = 0
            for domain in tool.domains.all():
                for question in domain.signalling_questions.all():
                    key = (str(domain.order), str(question.order))
                    if key in rob2_explanations:
                        question.explanation = rob2_explanations[key]
                        question.save()
                        updated_count += 1
                        self.stdout.write(
                            f"Updated explanation for Domain {domain.order}, Question {question.order}"
                        )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully added explanations to {updated_count} RoB 2.0 signalling questions'
                )
            )
            
        except AssessmentTool.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('RoB 2.0 parallel trial tool not found. Please run setup_rob2_data first.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'An error occurred: {str(e)}')
            )
