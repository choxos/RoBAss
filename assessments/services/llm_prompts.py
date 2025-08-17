"""
LLM Prompt Templates for Risk of Bias Assessment

This module contains comprehensive prompt templates for each RoB 2.0 domain
with detailed instructions and examples to ensure accurate LLM assessment.
"""

from typing import Dict, List
import json


class RoB2PromptTemplates:
    """Comprehensive prompt templates for RoB 2.0 assessment"""
    
    def __init__(self):
        self.system_prompt = self._get_system_prompt()
        self.domain_prompts = self._get_domain_prompts()
    
    def _get_system_prompt(self) -> str:
        """System prompt that defines the LLM's role and behavior"""
        return """You are an expert systematic reviewer and methodologist specializing in Risk of Bias assessment using the Cochrane RoB 2.0 tool for randomized controlled trials.

Your task is to carefully analyze the provided research article and answer specific signalling questions for risk of bias assessment. You must:

1. **Be Precise and Evidence-Based**: Base all responses strictly on information provided in the article text
2. **Use Exact RoB 2.0 Response Options**: Only use these response options:
   - "Yes" (Y)
   - "Probably Yes" (PY) 
   - "Probably No" (PN)
   - "No" (N)
   - "No Information" (NI)

3. **Provide Clear Justifications**: For each answer, provide specific quotes or references from the article
4. **Follow RoB 2.0 Algorithm**: Use the official Cochrane RoB 2.0 guidance for parallel trials
5. **Be Conservative**: When information is unclear or ambiguous, lean toward "No Information" rather than guessing

**Important Guidelines:**
- Read the entire article carefully before responding
- Focus on methodological aspects, not clinical findings
- Look for information in Methods, supplementary materials, protocol references, and trial registrations mentioned
- Consider what is explicitly stated vs. what might be implied
- Be aware that some information might be in appendices, supplements, or referenced protocols"""

    def _get_domain_prompts(self) -> Dict[str, Dict]:
        """Get detailed prompts for each RoB 2.0 domain"""
        return {
            "domain_1": {
                "title": "Domain 1: Risk of bias arising from the randomization process",
                "description": "This domain addresses whether the allocation sequence was random and adequately concealed, and whether baseline differences suggest problems with randomization.",
                "questions": [
                    {
                        "id": "1.1",
                        "text": "Was the allocation sequence random?",
                        "guidance": """Look for explicit mention of randomization methods. Consider:

**Answer "Yes" if:**
- Computer-generated random sequence is mentioned
- Random number tables are used  
- Coin flipping, dice rolling, or drawing lots is described
- Block randomization, stratified randomization with random component
- Central randomization service is used

**Answer "Probably Yes" if:**
- "Randomized" is stated but method not specified, and baseline characteristics appear balanced
- Central allocation without explicit randomization method mentioned

**Answer "No" if:**  
- Alternation (every other participant)
- Assignment by date of birth, hospital record number, or other systematic method
- Physician or patient preference determines allocation
- Any non-random systematic approach is described

**Answer "Probably No" if:**
- Method is unclear but systematic approach is suspected
- Significant baseline imbalances suggest non-random allocation

**Answer "No Information" if:**
- No information provided about randomization method
- Only states "randomized" without any details or supporting evidence

**Key search terms to look for:** randomization, random sequence, computer-generated, random number, block randomization, stratification, central randomization"""
                    },
                    {
                        "id": "1.2", 
                        "text": "Was the allocation sequence concealed until participants were enrolled and assigned?",
                        "guidance": """Look for methods that prevented selection bias by ensuring those enrolling participants couldn't predict upcoming allocations.

**Answer "Yes" if:**
- Central randomization (by phone, web-based, pharmacy)
- Sequentially numbered, opaque, sealed envelopes (SNOSE)
- Coded/numbered containers dispensed serially  
- On-site computer with password protection
- Other methods ensuring unpredictability until assignment

**Answer "Probably Yes" if:**
- Central allocation mentioned without full details
- Pharmacy randomization without details
- "Concealed allocation" stated with reasonable method implied

**Answer "No" if:**
- Open random allocation schedule/list
- Envelopes not opaque or sealed
- Alternation or other predictable methods
- Assignment based on patient characteristics available at enrollment

**Answer "Probably No" if:**
- Method described suggests prediction was possible
- Significant baseline imbalances suggesting selection bias

**Answer "No Information" if:**
- No information about concealment provided
- Only mentions randomization without concealment details

**Key search terms:** allocation concealment, sealed envelopes, opaque envelopes, central randomization, pharmacy randomization, coded containers, computer randomization"""
                    },
                    {
                        "id": "1.3",
                        "text": "Did baseline differences suggest a problem with the randomization process?",
                        "guidance": """Examine baseline characteristics tables and text for imbalances that are unlikely to occur by chance.

**Answer "Yes" if:**
- Large, clinically important imbalances in key prognostic factors
- Statistical tests of baseline characteristics show p<0.05 for important variables
- Authors acknowledge concerning baseline imbalances
- Imbalances that would be very unlikely by chance alone

**Answer "Probably Yes" if:**
- Moderate imbalances in several characteristics
- Some concerning differences but not clearly problematic
- Authors note imbalances but don't consider them problematic

**Answer "No" if:**
- Baseline characteristics appear well balanced
- Any minor differences appear consistent with chance variation
- Authors explicitly state groups were comparable at baseline

**Answer "Probably No" if:**
- Minor imbalances that could reasonably be due to chance
- Most characteristics balanced with few small differences

**Answer "No Information" if:**
- No baseline characteristics table provided
- Insufficient information to assess balance
- Characteristics presented but unclear if imbalanced

**What to look for:** Tables of baseline characteristics, p-values for baseline comparisons, author comments on group comparability, differences in age, sex, disease severity, comorbidities, or other prognostic factors"""
                    }
                ]
            },
            "domain_2": {
                "title": "Domain 2: Risk of bias due to deviations from intended interventions", 
                "description": "This domain addresses whether participants and personnel were blinded, whether deviations from intended intervention occurred, and whether analysis was appropriate.",
                "questions": [
                    {
                        "id": "2.1",
                        "text": "Were participants aware of their assigned intervention during the trial?",
                        "guidance": """Assess whether participants knew which treatment they were receiving.

**Answer "Yes" if:**
- Open-label study explicitly stated
- Single-blind with only assessors blinded
- Participants necessarily aware due to intervention nature (surgery vs. medication)
- Different administration routes/frequencies making blinding impossible
- Unblinding occurred and was not re-established

**Answer "Probably Yes" if:**
- Blinding attempted but likely ineffective (e.g., obvious side effects)
- Partial unblinding occurred for significant portion of participants
- Blinding method inadequate for the intervention

**Answer "No" if:**
- Double-blind or participant-blind explicitly stated with credible method
- Identical placebos used with matching appearance/taste
- Effective blinding procedures described and maintained
- Blinding assessment shows successful masking

**Answer "Probably No" if:**
- Blinding stated but method not fully described
- Some blinding procedures in place that likely worked
- No evidence of unblinding

**Answer "No Information" if:**
- No information about participant blinding provided
- Unclear whether participants were aware

**Key terms:** double-blind, single-blind, open-label, placebo, blinding, masking, participant awareness"""
                    },
                    {
                        "id": "2.2",
                        "text": "Were carers and people delivering the interventions aware of participants' assigned intervention?",
                        "guidance": """Assess awareness of healthcare providers, investigators, and study staff.

**Answer "Yes" if:**
- Open-label design
- Single-blind with only participants or assessors blinded
- Care providers necessarily aware (surgical vs. medical intervention)
- Different training/procedures required for each arm
- Staff unblinding occurred

**Answer "Probably Yes" if:**
- Blinding attempted but likely compromised
- Some staff necessarily aware while others blinded
- Inadequate blinding procedures for care providers

**Answer "No" if:**
- Double-blind with care providers explicitly blinded
- Identical interventions administered by blinded staff
- Effective masking procedures for care delivery
- Blinding maintained throughout study

**Answer "Probably No" if:**
- Blinding described but some uncertainty about effectiveness
- Most care providers likely blinded with good procedures

**Answer "No Information" if:**
- No information about care provider blinding
- Unclear who was aware of assignments

**Consider:** Doctors, nurses, research coordinators, pharmacists, other healthcare staff"""
                    },
                    {
                        "id": "2.3",
                        "text": "Were there deviations from the intended intervention beyond what would be expected in usual practice?",
                        "guidance": """Look for systematic differences in how interventions were delivered between groups.

**Answer "Yes" if:**
- Systematic differences in intervention delivery described
- Protocol violations affecting one group more than others
- Different monitoring, care, or procedures between groups
- Contamination or crossover affecting intervention delivery

**Answer "Probably Yes" if:**
- Some evidence of differential intervention delivery
- Minor protocol deviations that may have affected outcomes
- Imbalanced adherence or compliance between groups

**Answer "No" if:**
- No deviations from protocol described
- Any deviations were balanced between groups
- Standard care was consistent across groups
- Protocol adherence was high and similar

**Answer "Probably No" if:**
- Minor deviations that appear balanced
- Good protocol adherence reported
- No obvious systematic differences

**Answer "No Information" if:**
- No information about protocol adherence or deviations
- Unclear whether interventions were delivered as intended

**Look for:** Protocol violations, adherence rates, crossovers, contamination, co-interventions, monitoring differences"""
                    },
                    {
                        "id": "2.4",
                        "text": "If deviations occurred, were they likely to have affected the outcome?",
                        "guidance": """Assess whether any identified deviations could meaningfully impact the outcome being measured.

**Answer "Yes" if:**
- Deviations directly related to the outcome mechanism
- Clinically important changes in intervention dosage/timing
- Crossovers or treatment switches affecting substantial numbers
- Co-interventions that could influence outcomes

**Answer "Probably Yes" if:**
- Deviations could plausibly affect outcomes
- Moderate impact deviations affecting some participants
- Unclear magnitude but potential for outcome impact

**Answer "No" if:**
- Deviations unrelated to outcome mechanisms
- Minor protocol violations with no clinical impact
- Administrative deviations not affecting treatment

**Answer "Probably No" if:**
- Deviations unlikely to meaningfully affect outcomes
- Small magnitude deviations
- Good biological rationale that deviations wouldn't impact results

**Answer "No Information" if:**
- Deviations described but impact on outcomes unclear
- No information to judge potential effects

**Note:** Only answer this if you answered "Yes" or "Probably Yes" to question 2.3"""
                    },
                    {
                        "id": "2.5",
                        "text": "If deviations occurred, were they similar between groups or were they imbalanced between groups?",
                        "guidance": """Assess whether deviations affected both groups similarly or disproportionately affected one group.

**Answer "Yes" if:**
- Deviations reported as balanced/similar between groups  
- Similar rates of protocol violations in both arms
- Comparable adherence/compliance rates
- Crossovers occurred in both directions with similar frequency

**Answer "Probably Yes" if:**
- Appears balanced but not explicitly stated
- Minor differences in deviation rates
- Overall pattern suggests balance

**Answer "No" if:**
- Clear imbalance in deviations between groups
- One group had substantially more violations
- Systematic bias in deviation patterns
- Unidirectional crossovers or differential adherence

**Answer "Probably No" if:**
- Some evidence of imbalance in deviations
- Differences in deviation patterns between groups
- One group appears more affected

**Answer "No Information" if:**
- Deviations mentioned but balance between groups not described
- Insufficient information to assess balance

**Note:** Only answer this if you answered "Yes" or "Probably Yes" to question 2.3"""
                    },
                    {
                        "id": "2.6",
                        "text": "Was an appropriate analysis used to estimate the effect of assignment to intervention?",
                        "guidance": """Assess whether the analysis followed intention-to-treat principles.

**Answer "Yes" if:**
- Intention-to-treat (ITT) analysis explicitly used
- All randomized participants analyzed in original groups
- Modified ITT with reasonable exclusions clearly justified
- Analysis included all available follow-up data

**Answer "Probably Yes" if:**
- ITT mentioned and appears to be implemented
- Most participants analyzed in randomized groups
- Exclusions minimal and unlikely to bias results

**Answer "No" if:**
- Per-protocol analysis only
- As-treated analysis that ignores randomization
- Substantial exclusions without ITT analysis
- Analysis based on treatment received rather than assignment

**Answer "Probably No" if:**
- Analysis method suggests departure from ITT principles
- Significant exclusions not following ITT
- Unclear but concerning analysis approach

**Answer "No Information" if:**
- Analysis method not clearly described
- Unclear whether ITT principles followed
- Insufficient information about analytical approach

**Key terms:** intention-to-treat, ITT, modified ITT, per-protocol, as-treated, analysis population"""
                    },
                    {
                        "id": "2.7",
                        "text": "If the analysis was inappropriate, was there potential for a substantial impact on the result?",
                        "guidance": """Assess whether analytical problems could meaningfully change conclusions.

**Answer "Yes" if:**
- Large numbers excluded from inappropriate analysis
- Per-protocol analysis with substantial crossovers/withdrawals
- Analysis method could change direction/magnitude of effect
- Differential exclusions between groups

**Answer "Probably Yes" if:**
- Moderate exclusions or analytical concerns
- Potential for bias but uncertain magnitude
- Some participants analyzed incorrectly

**Answer "No" if:**
- Minor analytical issues unlikely to change conclusions
- Small numbers affected by inappropriate analysis
- Sensitivity analyses show robust results

**Answer "Probably No" if:**
- Analytical issues present but limited impact expected
- Most participants correctly analyzed

**Answer "No Information" if:**
- Impact of analytical problems unclear
- Insufficient information to judge potential bias

**Note:** Only answer this if you answered "No" or "Probably No" to question 2.6"""
                    }
                ]
            },
            "domain_3": {
                "title": "Domain 3: Risk of bias due to missing outcome data",
                "description": "This domain addresses whether outcome data were available for all participants and whether missingness could bias results.",
                "questions": [
                    {
                        "id": "3.1",
                        "text": "Were outcome data available for all, or nearly all, participants?",
                        "guidance": """Assess completeness of outcome data for the result being evaluated.

**Answer "Yes" if:**
- All randomized participants have outcome data
- Missing data <5% with no differential dropout
- Complete follow-up explicitly reported
- Any missing data clearly inconsequential

**Answer "Probably Yes" if:**
- Missing data 5-10% with balanced reasons
- Nearly complete follow-up with minor losses
- Missing data unlikely to affect conclusions

**Answer "No" if:**
- Substantial missing data (>20%)
- High dropout rates affecting outcome assessment
- Differential missing data between groups
- Large amount of outcome data unavailable

**Answer "Probably No" if:**
- Moderate missing data (10-20%) 
- Some concern about dropout patterns
- Missing data could potentially affect results

**Answer "No Information" if:**
- No information about missing data provided
- Unclear how many participants had outcome data
- Follow-up rates not reported

**Look for:** CONSORT diagrams, follow-up rates, dropout numbers, loss to follow-up, withdrawn participants"""
                    },
                    {
                        "id": "3.2",
                        "text": "Is there evidence that the result was not biased by missing outcome data?",
                        "guidance": """Look for evidence that missing data did not introduce bias.

**Answer "Yes" if:**
- Sensitivity analyses show robust results with missing data
- Imputation methods used with consistent results
- Missing data analysis demonstrates no bias
- Reasons for missingness unrelated to outcome

**Answer "Probably Yes" if:**
- Some evidence that missing data didn't affect results
- Reasonable imputation approach used
- Missing data patterns don't suggest bias

**Answer "No" if:**
- No evidence provided that missingness was unbiased
- Missing data clearly related to outcomes
- No sensitivity analyses for missing data
- Informative dropout patterns evident

**Answer "Probably No" if:**
- Limited evidence about missing data bias
- Some concern about missingness patterns
- Inadequate handling of missing data

**Answer "No Information" if:**
- No information about potential bias from missing data
- No analysis of missing data patterns provided

**Look for:** Sensitivity analyses, imputation methods, missing data analysis, dropout reasons, MCAR/MAR assumptions"""
                    },
                    {
                        "id": "3.3",
                        "text": "Could missingness in the outcome depend on its true value?",
                        "guidance": """Assess whether missing data mechanism could be related to outcome values.

**Answer "Yes" if:**
- Participants with poor outcomes more likely to dropout
- Side effects causing withdrawal related to efficacy
- Disease progression affecting ability to provide outcomes
- Subjective outcomes where participant state affects reporting

**Answer "Probably Yes" if:**
- Some plausible connection between outcome and missingness
- Patient-reported outcomes with differential dropout
- Clinical scenarios where sicker patients drop out

**Answer "No" if:**
- Missingness clearly unrelated to outcome (geographic move, protocol violation)
- Objective outcomes measured at specific time points
- Administrative censoring unrelated to health status
- Missing completely at random (MCAR) explicitly tested

**Answer "Probably No" if:**
- Unlikely connection between outcome and missingness
- Good evidence that dropout reasons unrelated to outcome
- Objective measurements less likely to be informative

**Answer "No Information" if:**
- No information about reasons for missing data
- Unclear what could cause differential missingness
- Missing data mechanism not discussed

**Consider:** Outcome type (subjective vs. objective), reasons for withdrawal, disease characteristics"""
                    },
                    {
                        "id": "3.4",
                        "text": "Is it likely that missingness in the outcome depended on its true value?",
                        "guidance": """Assess probability that missing data is informative (MNAR - Missing Not At Random).

**Answer "Yes" if:**
- Clear evidence that outcome values influenced dropout
- Participants with poor outcomes systematically missing
- Side effects causing withdrawal directly related to efficacy endpoint  
- Strong biological plausibility for informative missingness

**Answer "Probably Yes" if:**
- Plausible mechanisms for informative missingness
- Some evidence suggesting outcome-dependent dropout
- Differential dropout rates between treatment groups

**Answer "No" if:**
- Strong evidence that missingness unrelated to outcomes
- Dropout reasons clearly unrelated to health status
- Successful testing for MCAR or MAR mechanisms
- Objective outcomes with non-informative censoring

**Answer "Probably No" if:**
- Unlikely that outcome values influenced dropout
- Most evidence suggests non-informative missingness
- Good support for MAR assumption

**Answer "No Information" if:**
- Insufficient evidence to judge missingness mechanism
- No analysis of potential informative missingness
- Unclear relationship between dropout and outcomes

**Note:** This is typically the most difficult question - be conservative and consider biological plausibility"""
                    }
                ]
            },
            "domain_4": {
                "title": "Domain 4: Risk of bias in measurement of the outcome",
                "description": "This domain addresses whether outcome assessment methods were appropriate and consistent, and whether assessors were blinded.",
                "questions": [
                    {
                        "id": "4.1",
                        "text": "Was the method of measuring the outcome inappropriate?",
                        "guidance": """Assess whether the outcome measurement method was valid and reliable.

**Answer "Yes" if:**
- Measurement method clearly inappropriate for the outcome
- Unvalidated instruments used for key outcomes
- Timing of assessment inappropriate (too early/late)
- Method lacks sensitivity to detect clinically important differences

**Answer "Probably Yes" if:**
- Some concerns about measurement validity
- Suboptimal timing or methodology
- Measurement approach has known limitations

**Answer "No" if:**
- Validated, appropriate measurement instruments
- Standard, accepted methods for the outcome
- Appropriate timing and frequency of assessment  
- Method suitable for detecting expected treatment effects

**Answer "Probably No" if:**
- Generally appropriate methods with minor concerns
- Standard approaches used with good rationale
- Methods adequate for study objectives

**Answer "No Information" if:**
- Insufficient information about measurement methods
- Outcome assessment procedures not described
- Unclear how outcomes were measured

**Look for:** Validated scales, standard procedures, measurement timing, assessment protocols"""
                    },
                    {
                        "id": "4.2",
                        "text": "Could measurement or ascertainment of the outcome have differed between intervention groups?",
                        "guidance": """Assess whether outcome measurement was consistent across treatment groups.

**Answer "Yes" if:**
- Different measurement methods used for different groups
- Different timing or frequency of assessments
- Systematic differences in measurement procedures
- Different personnel assessing different groups

**Answer "Probably Yes" if:**
- Some indication of differential measurement
- Minor differences in assessment procedures
- Potential for systematic measurement differences

**Answer "No" if:**
- Identical measurement procedures for all groups
- Same instruments, timing, and personnel
- Standardized protocols followed consistently
- No evidence of differential measurement

**Answer "Probably No" if:**
- Likely similar measurement across groups
- Standard protocols appear consistently applied
- No obvious reasons for differential measurement

**Answer "No Information" if:**
- No information about measurement consistency
- Unclear whether procedures were the same across groups
- Assessment methods not sufficiently described

**Consider:** Measurement instruments, assessment timing, personnel, procedures, protocols"""
                    },
                    {
                        "id": "4.3",
                        "text": "Were outcome assessors aware of the intervention received?",
                        "guidance": """Assess whether those measuring outcomes knew participant treatment assignments.

**Answer "Yes" if:**
- Open-label study with unblinded assessors
- Assessors necessarily aware (surgical vs. medical outcomes)
- Blinding of assessors explicitly not attempted
- Assessors were treating clinicians who knew assignments

**Answer "Probably Yes" if:**
- Likely that assessors could determine assignments
- Partial blinding that probably failed
- Assessment by care providers who knew treatments

**Answer "No" if:**
- Outcome assessors explicitly blinded to treatment
- Independent, masked assessment clearly described
- Objective outcomes measured by blinded personnel
- Successful blinding verification described

**Answer "Probably No" if:**
- Assessor blinding attempted and likely successful
- Independent assessment with blinding procedures
- No evidence of unblinding

**Answer "No Information" if:**
- No information about assessor blinding
- Unclear who performed outcome assessments
- Blinding status of assessors not described

**Key terms:** blinded assessors, independent assessment, masked evaluation, outcome assessor awareness"""
                    },
                    {
                        "id": "4.4",
                        "text": "Could assessment of the outcome have been influenced by knowledge of intervention received?",
                        "guidance": """Assess potential for bias if assessors knew treatment assignments.

**Answer "Yes" if:**
- Subjective outcomes that could be influenced by knowledge
- Assessor expectations could affect measurements
- Outcomes requiring clinical judgment or interpretation
- Patient-reported outcomes where patient knowledge matters

**Answer "Probably Yes" if:**
- Some potential for assessment bias
- Partly subjective outcomes
- Moderate potential for influence

**Answer "No" if:**
- Completely objective outcomes (lab values, survival, imaging)
- Automated or standardized measurements
- No room for subjective interpretation
- Hard clinical endpoints

**Answer "Probably No" if:**
- Mostly objective outcomes with minimal subjective component
- Standardized procedures limiting bias potential
- Limited opportunity for influence

**Answer "No Information" if:**
- Unclear whether outcome assessment could be influenced
- Insufficient information about outcome subjectivity
- Cannot determine potential for bias

**Consider:** Outcome subjectivity, measurement procedures, potential for assessor bias"""
                    },
                    {
                        "id": "4.5",
                        "text": "Is it likely that assessment of the outcome was influenced by knowledge of intervention received?",
                        "guidance": """Assess probability that assessor knowledge actually biased outcome measurement.

**Answer "Yes" if:**
- Clear evidence of assessment bias
- Subjective outcomes assessed by unblinded, biased assessors
- Systematic differences in assessment stringency
- Strong potential for and evidence of bias

**Answer "Probably Yes" if:**
- Moderate likelihood of assessment bias
- Subjective outcomes with unblinded assessors
- Some evidence suggesting biased assessment

**Answer "No" if:**
- No evidence of assessment bias despite potential
- Objective outcomes preventing bias
- Blinded assessment successfully maintained
- Multiple safeguards against bias

**Answer "Probably No" if:**
- Unlikely that bias occurred despite potential
- Good procedures to minimize bias
- Limited evidence of actual bias

**Answer "No Information" if:**
- Cannot determine whether bias actually occurred
- Insufficient evidence about assessment quality
- Unclear impact of potential bias

**Note:** Consider both potential for bias (4.4) and likelihood it actually occurred"""
                    }
                ]
            },
            "domain_5": {
                "title": "Domain 5: Risk of bias in selection of the reported result",
                "description": "This domain addresses whether results were selected from multiple eligible outcomes or analyses based on the results.",
                "questions": [
                    {
                        "id": "5.1", 
                        "text": "Were the data that produced this result analysed in accordance with a pre-specified analysis plan?",
                        "guidance": """Assess whether the analysis followed a predetermined plan.

**Answer "Yes" if:**
- Published protocol or statistical analysis plan referenced
- Trial registry entry with detailed analysis plan
- Clear evidence of pre-specified analysis approach
- Methods section describes analysis plan prospectively

**Answer "Probably Yes" if:**
- Some evidence of pre-specification
- Methods suggest advance planning
- Standard analysis approach for this type of study

**Answer "No" if:**
- No evidence of pre-specified analysis plan
- Post-hoc analyses clearly described
- Analysis appears data-driven
- Methods suggest analyses were not planned

**Answer "Probably No" if:**
- Limited evidence of pre-specification
- Some analyses appear exploratory
- Unclear whether plan was predetermined

**Answer "No Information" if:**
- No information about analysis planning
- Unclear whether analyses were pre-specified
- No reference to protocols or analysis plans

**Look for:** Trial registration, published protocols, statistical analysis plans, methods descriptions"""
                    },
                    {
                        "id": "5.2",
                        "text": "Was the selected result likely to have been selected from multiple eligible outcome measurements?",
                        "guidance": """Assess whether the reported result was chosen from multiple possible outcome measures.

**Answer "Yes" if:**
- Multiple measurement instruments used but only favorable ones reported
- Different time points measured but only significant ones reported
- Various scales available but selective reporting evident
- Clear evidence of outcome measurement selection

**Answer "Probably Yes" if:**
- Some indication of selective outcome measurement reporting
- Multiple measures mentioned but not all reported
- Inconsistent reporting across similar outcomes

**Answer "No" if:**
- All measured outcomes reported
- Clear rationale for outcome selection
- Consistent with protocol-specified measurements
- No evidence of selective measurement reporting

**Answer "Probably No" if:**
- Appears that most/all measurements reported
- No obvious signs of selective reporting
- Reasonable outcome measurement approach

**Answer "No Information" if:**
- Cannot determine if multiple measurements were available
- Insufficient information about outcome measurement choices
- Unclear what other measurements might have been possible

**Consider:** Multiple scales, different time points, various measurement methods"""
                    },
                    {
                        "id": "5.3",
                        "text": "Was the selected result likely to have been selected from multiple analyses?",
                        "guidance": """Assess whether the reported result was chosen from multiple possible analyses.

**Answer "Yes" if:**
- Multiple statistical approaches mentioned but only significant ones reported
- Evidence of data mining or p-hacking
- Subgroup analyses reported only when significant
- Clear selection from multiple analytical approaches

**Answer "Probably Yes" if:**
- Some indication of selective analysis reporting
- Multiple analyses mentioned but incomplete reporting
- Focus on significant results with other analyses downplayed

**Answer "No" if:**
- All planned analyses reported
- Consistent with pre-specified analysis plan
- No evidence of selective analysis reporting
- Comprehensive reporting of analytical approaches

**Answer "Probably No" if:**
- Appears most analyses reported
- No clear evidence of selective reporting
- Standard analytical approach used

**Answer "No Information" if:**
- Cannot determine what other analyses were performed
- Insufficient information about analytical choices
- Unclear whether multiple approaches were considered

**Look for:** Multiple statistical tests, subgroup analyses, different analytical methods, post-hoc analyses"""
                    }
                ]
            }
        }

    def generate_assessment_prompt(self, study_text: str, domain: str = None) -> str:
        """Generate a complete assessment prompt for a specific domain or all domains"""
        
        if domain and domain in self.domain_prompts:
            # Single domain assessment
            domain_info = self.domain_prompts[domain]
            
            prompt = f"""{self.system_prompt}

## ARTICLE TEXT TO ANALYZE:
{study_text}

## ASSESSMENT TASK:
You are now assessing **{domain_info['title']}**

{domain_info['description']}

Please answer each of the following signalling questions based strictly on the information in the article above. For each question:
1. Provide your answer using EXACTLY one of: "Yes", "Probably Yes", "Probably No", "No", or "No Information"
2. Provide a brief justification with specific quotes or references from the article
3. If no relevant information is found, answer "No Information"

## SIGNALLING QUESTIONS:
"""
            
            for i, question in enumerate(domain_info['questions'], 1):
                prompt += f"""
### Question {question['id']}: {question['text']}

**Guidance:**
{question['guidance']}

**Your Assessment:**
- **Answer:** [Your answer here]
- **Justification:** [Specific evidence from the article]

"""
            
        else:
            # Full assessment prompt
            prompt = f"""{self.system_prompt}

## ARTICLE TEXT TO ANALYZE:
{study_text}

## ASSESSMENT TASK:
Please conduct a complete Risk of Bias assessment for this randomized controlled trial using the RoB 2.0 tool. You will assess all five domains systematically.

For each signalling question:
1. Provide your answer using EXACTLY one of: "Yes", "Probably Yes", "Probably No", "No", or "No Information"  
2. Provide a brief justification with specific quotes or references from the article
3. If no relevant information is found, answer "No Information"

Please format your response as JSON with the following structure:
```json
{
    "domain_1": {
        "1.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "1.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "1.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    },
    "domain_2": {
        "2.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        ...
    },
    ...
}
```

## ASSESSMENT DOMAINS AND QUESTIONS:
"""
            
            for domain_key, domain_info in self.domain_prompts.items():
                prompt += f"""
### {domain_info['title']}
{domain_info['description']}

"""
                for question in domain_info['questions']:
                    prompt += f"""
**{question['id']}. {question['text']}**
{question['guidance']}

"""
        
        return prompt

    def generate_quick_assessment_prompt(self, study_text: str, extracted_content: Dict) -> str:
        """Generate a prompt using pre-extracted relevant content for efficiency"""
        
        prompt = f"""{self.system_prompt}

## EXTRACTED RELEVANT CONTENT:

**Randomization Content:**
{chr(10).join(extracted_content.get('randomization', []))}

**Blinding Content:** 
{chr(10).join(extracted_content.get('blinding', []))}

**Deviations Content:**
{chr(10).join(extracted_content.get('deviations', []))}

**Missing Data Content:**
{chr(10).join(extracted_content.get('missing_data', []))}

**Outcome Measurement Content:**
{chr(10).join(extracted_content.get('outcome_measurement', []))}

**Selective Reporting Content:**
{chr(10).join(extracted_content.get('selective_reporting', []))}

## FULL ARTICLE TEXT:
{study_text}

## ASSESSMENT TASK:
Based on the extracted content above and the full article text, please provide a complete RoB 2.0 assessment. The extracted content highlights potentially relevant sentences, but you should also consider the full article context.

Please respond in JSON format with your assessment for all 22 signalling questions across the 5 domains.

```json
{
    "domain_1": {
        "1.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "1.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "1.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    },
    "domain_2": {
        "2.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "2.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "2.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "2.4": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "2.5": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "2.6": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "2.7": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    },
    "domain_3": {
        "3.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "3.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "3.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "3.4": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    },
    "domain_4": {
        "4.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "4.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "4.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "4.4": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "4.5": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    },
    "domain_5": {
        "5.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "5.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "5.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    }
}
```
"""
        return prompt
