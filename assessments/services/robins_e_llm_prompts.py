"""
LLM Prompt Templates for ROBINS-E (Risk of Bias in Non-randomized Studies of Exposures) Assessment

This module contains comprehensive prompt templates for each ROBINS-E domain
with detailed instructions and examples to ensure accurate LLM assessment.
"""

from typing import Dict, List
import json


class ROBINSEPromptTemplates:
    """Comprehensive prompt templates for ROBINS-E assessment"""
    
    def __init__(self):
        self.system_prompt = self._get_system_prompt()
        self.domain_prompts = self._get_domain_prompts()
    
    def _get_system_prompt(self) -> str:
        """System prompt that defines the LLM's role and behavior"""
        return """You are an expert systematic reviewer and methodologist specializing in Risk of Bias assessment using the ROBINS-E tool for non-randomized studies of exposures.

Your task is to carefully analyze the provided research article and answer specific signalling questions for risk of bias assessment. You must:

1. **Be Precise and Evidence-Based**: Base all responses strictly on information provided in the article text
2. **Use Exact ROBINS-E Response Options**: Only use these response options:
   - "Yes" (Y)
   - "Probably Yes" (PY) 
   - "Probably No" (PN)
   - "No" (N)
   - "No Information" (NI)

3. **Provide Clear Justifications**: For each answer, provide specific quotes or references from the article
4. **Follow ROBINS-E Methodology**: Use the official guidance for non-randomized studies of exposures
5. **Be Conservative**: When information is unclear or ambiguous, lean toward "No Information" rather than guessing

**Important Guidelines:**
- Read the entire article carefully before responding
- Focus on methodological aspects, not clinical or epidemiological findings
- Look for information in Methods, supplementary materials, protocol references, and prior publications mentioned
- Consider what is explicitly stated vs. what might be implied
- Be aware that some information might be in appendices, supplements, or referenced protocols"""

    def _get_domain_prompts(self) -> Dict[str, Dict]:
        """Get detailed prompts for each ROBINS-E domain"""
        return {
            "domain_1": {
                "title": "Domain 1: Risk of bias due to confounding",
                "description": "This domain addresses whether baseline differences between exposure groups that affect the outcome were adequately controlled for in the analysis.",
                "questions": [
                    {
                        "id": "1.1",
                        "text": "Was the analysis method for the main exposure appropriate?",
                        "guidance": """Look for information about the statistical analysis method used to estimate the effect of the exposure on the outcome.

**Answer "Yes" if:**
- Appropriate analytical method for the study design (e.g., regression models for confounding control)
- Suitable statistical approach for the research question (e.g., propensity score methods, instrumental variables)
- Methods address the specific challenges of the exposure-outcome relationship
- Transparent reporting of analysis strategy with clear rationale

**Answer "Probably Yes" if:**
- Generally appropriate methods but with minor limitations
- Standard approaches used for similar research questions
- Some details missing but overall approach seems appropriate

**Answer "No" if:**
- Clearly inappropriate analysis method for the study design
- Fundamental flaws in statistical approach
- Analysis fails to account for study design features (e.g., matching, clustering)
- Methods that cannot address the research question

**Answer "Probably No" if:**
- Questionable analytical choices with potential to bias results
- Suboptimal methods when better approaches were feasible
- Inadequate description with concerning elements

**Answer "No Information" if:**
- Statistical methods not described
- Insufficient detail to judge appropriateness
- Unclear how exposure effects were estimated

**Key terms to look for:** regression analysis, propensity score, instrumental variable, statistical adjustment, multivariate analysis, matching, stratification, weighting"""
                    },
                    {
                        "id": "1.2",
                        "text": "Were the important confounding factors identified and controlled for?",
                        "guidance": """Look for information about whether all important confounding factors that could affect both the exposure and outcome have been identified and appropriately controlled for.

**Answer "Yes" if:**
- Comprehensive list of relevant confounders identified and controlled
- Adjustment for all major known confounders in the field
- Careful consideration of potential confounding pathways
- Multiple approaches to address confounding (e.g., adjustment + sensitivity analysis)

**Answer "Probably Yes" if:**
- Most important confounders controlled for
- Reasonable approach to confounder selection
- Some minor potential confounders may be missing but unlikely to substantially affect results

**Answer "No" if:**
- Critical known confounders clearly missing from analysis
- No adjustment for important confounders
- Confounders identified but not properly controlled for
- Obvious confounding pathways ignored

**Answer "Probably No" if:**
- Incomplete confounder control with potential to affect results
- Questionable selection of confounders
- Important variables likely missing

**Answer "No Information" if:**
- No information on confounders considered
- Unclear which factors were controlled for
- Cannot determine confounding control strategy

**Key confounders often include:** age, sex/gender, socioeconomic status, comorbidities, baseline health status, other exposures, lifestyle factors, calendar time"""
                    },
                    {
                        "id": "1.3",
                        "text": "Were confounding factors measured validly and reliably?",
                        "guidance": """Look for information about the quality of measurement for confounding factors included in the analysis.

**Answer "Yes" if:**
- Validated instruments or standard methods used to measure confounders
- Objective measures from reliable sources (medical records, registries)
- Clear reporting of measurement procedures
- Multiple sources used to verify important confounders
- Appropriate timing of confounder measurement (prior to exposure)

**Answer "Probably Yes" if:**
- Generally acceptable measurement methods
- Mostly standard approaches with some limitations
- Reasonable measurement timing relative to exposure

**Answer "No" if:**
- Clearly inadequate measurement methods for key confounders
- Self-reported data for confounders requiring objective measurement
- Substantial measurement error likely
- Inappropriate timing of measurement (after exposure or outcome)

**Answer "Probably No" if:**
- Questionable measurement quality for important confounders
- Some measures likely to have significant error
- Limited information suggesting poor measurement

**Answer "No Information" if:**
- No details on how confounders were measured
- Cannot determine measurement methods
- Unclear timing of confounder assessment

**Look for:** measurement tool descriptions, data sources for confounders, timing of measurements, validation studies cited, reliability information"""
                    },
                    {
                        "id": "1.4",
                        "text": "Were any variables that were measured after the start of exposure controlled for?",
                        "guidance": """Look for information about whether the analysis inappropriately controlled for variables that were measured or occurred after exposure began (potential mediators).

**Answer "Yes" if:**
- Clear evidence that post-exposure variables were included in the main analysis model
- Adjustment for variables on the causal pathway between exposure and outcome
- Control for potential mediators without appropriate mediation analysis methods
- Explicit statement about controlling for post-exposure variables

**Answer "Probably Yes" if:**
- Some variables appear to be post-exposure and included in adjustment
- Timing of variable measurement suggests post-exposure assessment
- Likely adjustment for variables affected by exposure

**Answer "No" if:**
- Explicit statement that only baseline/pre-exposure variables were used for adjustment
- Clear temporal separation of confounder measurement before exposure
- Appropriate handling of time-varying confounding if present (e.g., marginal structural models)
- Careful consideration of causal pathways

**Answer "Probably No" if:**
- Mostly pre-exposure variables used but some uncertainty
- Generally appropriate approach to covariate selection
- Minor concerns about potential post-exposure variables

**Answer "No Information" if:**
- Timing of variable measurement not reported
- Cannot determine when confounders were measured relative to exposure
- Unclear which variables were included in adjustment models

**Post-exposure variables to watch for:** Physiological parameters that could change after exposure, intermediate health states, concurrent medications/treatments initiated after exposure, lifestyle changes in response to exposure"""
                    },
                    {
                        "id": "1.5",
                        "text": "Do negative controls or other approaches suggest serious uncontrolled confounding?",
                        "guidance": """Look for information about whether the authors used negative control analyses, sensitivity analyses, or other approaches to assess uncontrolled confounding.

**Answer "Yes" if:**
- Negative control analyses show associations where none would be expected
- E-value or other quantitative bias analysis suggests substantial uncontrolled confounding
- Sensitivity analyses indicate results are highly vulnerable to unmeasured confounding
- Authors acknowledge serious confounding concerns that remain unaddressed

**Answer "Probably Yes" if:**
- Some concerning results from negative controls or sensitivity analyses
- Quantitative bias analysis suggests possible meaningful confounding
- Pattern of results consistent with potential confounding

**Answer "No" if:**
- Negative control analyses show no unexpected associations
- E-value or quantitative bias analysis suggests results robust to unmeasured confounding
- Multiple sensitivity analyses support main findings
- Authors convincingly address potential unmeasured confounding concerns

**Answer "Probably No" if:**
- Limited but reassuring sensitivity analyses
- Some effort to address unmeasured confounding with generally supportive results
- No major indications of uncontrolled confounding

**Answer "No Information" if:**
- No negative controls, E-values, or sensitivity analyses reported
- No assessment of potential unmeasured confounding
- Cannot determine if uncontrolled confounding was evaluated

**Look for:** negative control outcomes/exposures, E-values, quantitative bias analysis, unmeasured confounder sensitivity analysis, multiple methods of confounder control with consistent results"""
                    }
                ]
            },
            "domain_2": {
                "title": "Domain 2: Risk of bias in measurement of exposures", 
                "description": "This domain addresses whether exposures were measured accurately, consistently, and without knowledge of outcome status.",
                "questions": [
                    {
                        "id": "2.1",
                        "text": "Could the exposure have been measured differently between groups being compared?",
                        "guidance": """Look for information about whether exposure measurement methods differed systematically between comparison groups.

**Answer "Yes" if:**
- Different measurement methods explicitly used for different groups
- Differential intensity of exposure assessment between groups
- Different data sources used for exposure information across groups
- Clear evidence of differential measurement procedures

**Answer "Probably Yes" if:**
- Likely differences in exposure measurement between groups
- Some indications of differential assessment methods
- Potential for systematic differences in measurement quality

**Answer "No" if:**
- Identical exposure measurement methods explicitly used for all groups
- Standardized procedures applied consistently across groups
- Objective exposure measures from same data source for all participants
- Clear protocols ensuring uniform assessment

**Answer "Probably No" if:**
- Generally consistent methods described
- Minor differences unlikely to introduce substantial bias
- Mostly standardized approach across groups

**Answer "No Information" if:**
- Insufficient details on exposure measurement methods
- Cannot determine if measurement differed between groups
- Unclear exposure assessment procedures

**Examples of differential measurement:** Different questionnaires/interviews for different groups, more intensive exposure assessment for one group, different staff collecting exposure data, different laboratory methods, different timing of exposure assessment"""
                    },
                    {
                        "id": "2.2", 
                        "text": "Were outcome assessors aware of the exposure status of study participants?",
                        "guidance": """Look for information about whether those assessing or classifying exposure status knew about participants' outcomes.

**Answer "Yes" if:**
- Explicit statement that exposure assessors knew outcome status
- Retrospective exposure assessment after outcomes developed
- Self-reported exposure after outcome occurrence
- Study design necessarily revealing outcome status to exposure assessors

**Answer "Probably Yes" if:**
- Likely awareness of outcomes during exposure assessment
- Study procedures suggesting knowledge of outcomes
- No mention of blinding in context where it would be expected

**Answer "No" if:**
- Explicit blinding of exposure assessors to outcome status
- Prospective exposure assessment before outcomes developed
- Objective exposure measures recorded independently of outcomes
- Clear temporal separation ensuring outcomes unknown during exposure assessment

**Answer "Probably No" if:**
- Procedures suggesting exposure assessment independent of outcomes
- Partial blinding or administrative separation of exposure and outcome assessment
- Design features limiting outcome knowledge during exposure assessment

**Answer "No Information" if:**
- No information about blinding or timing of exposure assessment relative to outcomes
- Cannot determine if exposure assessors knew about outcomes
- Unclear procedures for exposure classification

**Look for:** blinding procedures, timing of exposure assessment relative to outcome determination, administrative separation of exposure and outcome assessment, use of pre-existing exposure records"""
                    },
                    {
                        "id": "2.3",
                        "text": "Could misclassification of exposure status have affected results?",
                        "guidance": """Look for information about the potential impact of exposure misclassification on study results.

**Answer "Yes" if:**
- Clear evidence of substantial exposure misclassification
- Validation sub-studies showing poor exposure classification accuracy
- Highly subjective or error-prone exposure measures without verification
- Likely differential misclassification between groups
- Self-reported exposure for conditions prone to recall bias

**Answer "Probably Yes" if:**
- Some evidence suggesting exposure misclassification
- Imprecise or indirect exposure measures
- Limited validation with concerning results
- Potential for recall or reporting biases

**Answer "No" if:**
- Highly accurate exposure measurement methods
- Validation studies confirming excellent classification performance
- Objective measures from reliable sources
- Multiple methods showing consistent exposure classification
- Appropriate steps to minimize and quantify potential misclassification

**Answer "Probably No" if:**
- Generally reliable methods with minor limitations
- Some validation supporting reasonable accuracy
- Standard approaches with acceptable performance in the field

**Answer "No Information" if:**
- No information about exposure measurement accuracy
- Cannot assess potential for misclassification
- No validation or evaluation of exposure measures reported

**Consider:** Validation studies, comparison with gold standards, reliability statistics (kappa, ICC), sensitivity analyses exploring misclassification, use of biomarkers or objective measures versus self-report"""
                    }
                ]
            },
            "domain_3": {
                "title": "Domain 3: Risk of bias in selection of participants into the study",
                "description": "This domain addresses whether selection into the study was related to both exposure and outcome, potentially biasing the exposure-outcome relationship.",
                "questions": [
                    {
                        "id": "3.1",
                        "text": "Was selection of participants into the study related to the exposure and likely influenced by the outcome or a cause of the outcome?",
                        "guidance": """Look for information about whether participant selection could have created an artificial association between exposure and outcome.

**Answer "Yes" if:**
- Clear evidence that selection was related to both exposure and outcome
- Selection criteria explicitly based on factors affected by both exposure and outcome
- Case-control design where exposure might influence case status
- Evident survivorship bias or incidence-prevalence bias
- Exclusion criteria removing participants differentially by both exposure and outcome

**Answer "Probably Yes" if:**
- Some indication that selection could be related to exposure and outcome
- Participation rates differing by factors linked to both exposure and outcome
- Potential for selection bias without clear evidence of its absence

**Answer "No" if:**
- Selection clearly independent of exposure and outcome
- Complete or representative sampling of source population
- Selection procedures explicitly designed to prevent bias
- Convincing evidence that selection factors unrelated to exposure-outcome relationship
- Appropriate design features that prevent selection bias

**Answer "Probably No" if:**
- Mostly appropriate selection procedures with minor limitations
- Generally representative sample with some restrictions unlikely to bias results
- Some selection factors but unlikely related to both exposure and outcome

**Answer "No Information" if:**
- Insufficient information about selection procedures
- Cannot determine relationship between selection, exposure and outcome
- Unclear sampling frame or selection criteria

**Look for:** Participation rates by exposure/outcome status, reasons for non-participation, comparison of participants vs. non-participants, selection flowcharts, explicit inclusion/exclusion criteria"""
                    },
                    {
                        "id": "3.2",
                        "text": "Were the methods of outcome assessment comparable between exposed and unexposed groups?",
                        "guidance": """Look for information about whether outcome assessment methods were consistent across exposure groups.

**Answer "Yes" if:**
- Explicitly different outcome assessment methods between exposure groups
- Different data sources used for outcomes in different exposure categories
- Different diagnostic criteria applied by exposure status
- Different follow-up procedures based on exposure

**Answer "Probably Yes" if:**
- Some evidence suggesting differential outcome assessment
- Procedures potentially leading to different assessment intensity
- Partial differences in outcome evaluation methods

**Answer "No" if:**
- Identical outcome assessment methods for all exposure groups
- Standardized protocols applied consistently regardless of exposure
- Blinded outcome assessment preventing differential procedures
- Clear evidence of comparable methods across groups

**Answer "Probably No" if:**
- Generally consistent methods with minor variations unlikely to bias results
- Standardized approach with limited exceptions
- Mostly comparable assessment procedures

**Answer "No Information" if:**
- Insufficient detail about outcome assessment methods
- Cannot determine if methods differed between exposure groups
- Unclear outcome assessment procedures

**Look for:** Standardized outcome definitions, consistent data sources across groups, uniform diagnostic criteria, similar follow-up schedules, blinded outcome assessment"""
                    },
                    {
                        "id": "3.3",
                        "text": "Was follow-up time likely to be sufficient for outcomes to occur?",
                        "guidance": """Look for information about whether the duration of follow-up was adequate and comparable between exposure groups.

**Answer "Yes" if:**
- Follow-up duration clearly sufficient for outcomes to develop
- Follow-up period aligned with known latency/induction periods
- Similar follow-up duration between exposure groups
- Appropriate time-to-event analysis accounting for variable follow-up

**Answer "Probably Yes" if:**
- Generally adequate follow-up with minor limitations
- Follow-up likely sufficient for most outcomes of interest
- Mostly comparable follow-up between groups

**Answer "No" if:**
- Follow-up clearly insufficient for outcomes to develop
- Follow-up duration shorter than known latency/induction periods
- Substantially different follow-up times between exposure groups
- Early termination preventing outcome ascertainment

**Answer "Probably No" if:**
- Questionable follow-up duration for some outcomes
- Some differential follow-up between groups
- Somewhat short follow-up relative to expected latency periods

**Answer "No Information" if:**
- No information about follow-up duration
- Cannot determine adequacy of follow-up period
- Unclear differences in follow-up between groups

**Consider:** Known latency periods for outcomes, median/mean follow-up duration, minimum follow-up time, distributions of follow-up by exposure status, time-to-event analyses"""
                    }
                ]
            },
            "domain_4": {
                "title": "Domain 4: Risk of bias due to post-exposure interventions",
                "description": "This domain addresses whether interventions or treatments received after exposure could have influenced outcomes differentially between exposure groups.",
                "questions": [
                    {
                        "id": "4.1",
                        "text": "Were post-exposure variables that could be affected by the exposure controlled for?",
                        "guidance": """Look for information about whether the analysis inappropriately controlled for variables that could be affected by the exposure (potential mediators).

**Answer "Yes" if:**
- Clear evidence of controlling for variables on the causal pathway
- Adjustment for mediating variables between exposure and outcome
- Analysis explicitly includes post-exposure factors affected by exposure
- Control for consequences or manifestations of the exposure

**Answer "Probably Yes" if:**
- Some indication of controlling for variables likely affected by exposure
- Partial adjustment for potential mediators
- Analysis approach suggesting mediator inclusion

**Answer "No" if:**
- Explicit avoidance of controlling for post-exposure variables affected by exposure
- Clear separation of confounders (adjusted for) from mediators (not adjusted for)
- Appropriate causal framework guiding variable selection
- Mediation analysis properly implemented if examining pathways

**Answer "Probably No" if:**
- Generally appropriate approach avoiding most post-exposure adjustment
- Minor concerns about potential mediator inclusion
- Mostly pre-exposure variables in adjustment models

**Answer "No Information" if:**
- Cannot determine which variables were included in adjustment
- Unclear timing of variables relative to exposure
- Insufficient information about analysis approach

**Examples of potential mediators:** Physiological changes caused by exposure, symptoms or conditions resulting from exposure, behavioral changes in response to exposure, intermediate outcomes on causal pathway"""
                    },
                    {
                        "id": "4.2",
                        "text": "Were there important differences in ancillary treatments between exposure groups?",
                        "guidance": """Look for information about whether other treatments or interventions differed systematically between exposure groups.

**Answer "Yes" if:**
- Clear evidence of differential treatment by exposure status
- Explicit reporting of different care patterns between groups
- Exposure directly influencing treatment decisions
- Protocol-specified different management by exposure group

**Answer "Probably Yes" if:**
- Some indication of potential treatment differences
- Plausible differential care based on study context
- Indirect evidence suggesting treatment variations

**Answer "No" if:**
- Explicit statement of similar treatment protocols regardless of exposure
- Evidence of standardized care across exposure groups
- Analysis accounting for any treatment differences
- Study design preventing differential treatment

**Answer "Probably No" if:**
- Generally similar treatment approaches with minor variations
- No major indications of differential care
- Context suggesting standardized management

**Answer "No Information" if:**
- No information about treatments or interventions
- Cannot determine if treatments differed between groups
- Unclear management approaches

**Look for:** Treatment protocols, co-interventions, medication use, preventive measures, supportive care, management guidelines, treatment standardization efforts"""
                    },
                    {
                        "id": "4.3",
                        "text": "Could differences in ancillary treatments have affected the outcome?",
                        "guidance": """Look for information about the potential impact of any treatment differences on the study outcomes.

**Answer "Yes" if:**
- Treatment differences directly related to study outcomes
- Differential treatments with known effects on the outcomes
- Magnitude of treatment differences likely to substantially affect results
- Author acknowledgment of treatment effects on outcomes

**Answer "Probably Yes" if:**
- Treatment differences possibly affecting outcomes
- Some relationship between treatments and outcomes of interest
- Potential for meaningful impact on results

**Answer "No" if:**
- Treatments unrelated to study outcomes
- Minimal treatment differences unlikely to affect results
- Analysis accounting for treatment effects
- Treatments with no known impact on outcomes studied

**Answer "Probably No" if:**
- Minor treatment variations with limited potential impact
- Treatments unlikely to substantially affect specific outcomes
- Generally similar management for factors influencing outcomes

**Answer "No Information" if:**
- Insufficient information about treatments or their effects
- Cannot assess relationship between treatments and outcomes
- Unclear potential impact of any treatment differences

**Consider:** Known effects of treatments on outcomes studied, magnitude of treatment differences, specific mechanisms by which treatments could influence results, subgroup or sensitivity analyses exploring treatment effects"""
                    }
                ]
            },
            "domain_5": {
                "title": "Domain 5: Risk of bias due to missing data",
                "description": "This domain addresses whether missing data on exposures, outcomes, or confounders could have biased the results.",
                "questions": [
                    {
                        "id": "5.1",
                        "text": "Were outcome data reasonably complete for all participants?",
                        "guidance": """Look for information about the extent of missing outcome data and whether this differed between exposure groups.

**Answer "Yes" if:**
- Complete or near-complete outcome data (>90-95%)
- Minimal missing data with unlikely impact on results
- Similar completeness across exposure groups
- Appropriate methods accounting for any missing data

**Answer "Probably Yes" if:**
- Generally good outcome completeness with some limitations
- Moderate missing data (10-20%) unlikely to substantially bias results
- Mostly similar missingness patterns across groups

**Answer "No" if:**
- Substantial missing outcome data (>20-30%)
- Markedly different missing data rates between exposure groups
- Clear evidence of informative missingness
- No appropriate methods to address missing data

**Answer "Probably No" if:**
- Concerning levels of missing data that could affect results
- Some differential missingness between groups
- Limited attempts to address missing data issues

**Answer "No Information" if:**
- No information about missing outcome data
- Cannot determine completeness of outcome ascertainment
- Unclear reporting of missing data patterns

**Look for:** CONSORT/STROBE flowcharts, attrition tables, numbers analyzed vs. enrolled, follow-up rates, missing data by exposure status, sensitivity analyses for missing data"""
                    },
                    {
                        "id": "5.2",
                        "text": "Were participants excluded due to missing data on exposure status?",
                        "guidance": """Look for information about whether participants were excluded from the study due to missing exposure information.

**Answer "Yes" if:**
- Explicit statement of excluding participants with missing exposure data
- Analysis limited to complete-case exposure information
- Substantial number of participants excluded due to missing exposure
- Different exclusion rates across outcome groups

**Answer "Probably Yes" if:**
- Some indication of exclusions due to missing exposure data
- Analytical approach suggesting complete-case analysis
- Likely differential exclusions by outcome status

**Answer "No" if:**
- Complete or near-complete exposure data for all participants
- Appropriate imputation or other methods for missing exposure data
- Explicit inclusion of all participants regardless of exposure data completeness
- Analysis methods accounting for missing exposure information

**Answer "Probably No" if:**
- Minimal exclusions due to missing exposure data
- Generally inclusive approach with limited exceptions
- Non-differential missing exposure data with appropriate handling

**Answer "No Information" if:**
- No information about missing exposure data
- Cannot determine if exclusions occurred due to missing exposure
- Unclear analytical approach to missing exposure data

**Look for:** Sample selection flowcharts, exclusion criteria mentioning missing data, analytical sample vs. eligible sample comparisons, methods for handling missing exposure data"""
                    },
                    {
                        "id": "5.3",
                        "text": "Were participants excluded due to missing data on important confounders?",
                        "guidance": """Look for information about whether participants were excluded from analysis due to missing confounder data.

**Answer "Yes" if:**
- Explicit complete-case analysis excluding those with missing confounder data
- Substantial exclusions due to missing covariates
- Different exclusion rates by exposure or outcome status
- Listwise deletion approach clearly stated

**Answer "Probably Yes" if:**
- Some indication of exclusions due to missing confounder data
- Analysis approach suggesting complete-case analysis
- Likely differential exclusions across comparison groups

**Answer "No" if:**
- Appropriate methods for handling missing confounder data (e.g., multiple imputation)
- Explicit inclusion of all participants regardless of confounder completeness
- Sensitivity analyses comparing complete-case and imputed results
- Minimal missing confounder data with unlikely impact

**Answer "Probably No" if:**
- Generally appropriate handling of missing confounder data
- Limited exclusions unlikely to substantially affect results
- Non-differential missing confounder patterns

**Answer "No Information" if:**
- No information about missing confounder data
- Cannot determine analytical approach to missing covariates
- Unclear whether exclusions occurred due to missing confounders

**Look for:** Statistical methods section describing handling of missing data, sample size discrepancies between univariate and adjusted analyses, multiple imputation methods, complete-case analysis statements"""
                    },
                    {
                        "id": "5.4",
                        "text": "Was the analysis method appropriate for handling missing data?",
                        "guidance": """Look for information about the statistical methods used to address missing data.

**Answer "Yes" if:**
- Appropriate modern methods for missing data (multiple imputation, maximum likelihood)
- Methods aligned with likely missing data mechanism (MCAR, MAR, MNAR)
- Sensitivity analyses exploring impact of missing data assumptions
- Comprehensive approach with thorough reporting

**Answer "Probably Yes" if:**
- Generally appropriate methods with some limitations
- Reasonable approach given study context and missing data patterns
- Some sensitivity analyses for missing data impact

**Answer "No" if:**
- Clearly inappropriate methods (e.g., single imputation for MAR/MNAR data)
- No attempt to address potentially impactful missing data
- Methods inconsistent with likely missing data mechanisms
- Approaches known to introduce bias (e.g., missing indicator method)

**Answer "Probably No" if:**
- Suboptimal approaches with potential to affect results
- Limited methods that don't fully address missing data concerns
- Inadequate sensitivity analyses for missing data impact

**Answer "No Information" if:**
- No description of methods for handling missing data
- Cannot determine analytical approach to missingness
- Unclear missing data mechanisms or handling

**Key methods to look for:** Multiple imputation, maximum likelihood estimation, inverse probability weighting, pattern mixture models, sensitivity analyses for missing not at random data, complete case analysis with missing completely at random justification"""
                    }
                ]
            },
            "domain_6": {
                "title": "Domain 6: Risk of bias in measurement of outcomes",
                "description": "This domain addresses whether outcomes were measured accurately, consistently, and without knowledge of exposure status.",
                "questions": [
                    {
                        "id": "6.1",
                        "text": "Could the outcome measure have been influenced by knowledge of the exposure received?",
                        "guidance": """Look for information about whether the outcome is subjective and could be influenced by awareness of exposure status.

**Answer "Yes" if:**
- Subjective outcome measure susceptible to expectation bias
- Patient-reported outcomes with awareness of exposure
- Clinician-assessed outcomes requiring judgment without blinding
- Outcomes explicitly influenced by knowledge of exposure (e.g., reporting bias)

**Answer "Probably Yes" if:**
- Somewhat subjective outcome measures
- Potential for expectation or detection bias
- Limited safeguards against bias for subjective components

**Answer "No" if:**
- Completely objective outcome unlikely to be influenced by knowledge
- Hard clinical endpoints (e.g., all-cause mortality, laboratory values)
- Outcomes from mandatory registries independent of study
- Outcome determination by automated systems without human judgment

**Answer "Probably No" if:**
- Mostly objective outcomes with minimal subjective components
- Outcomes unlikely to be substantially influenced by knowledge
- Robust outcome definitions minimizing subjectivity

**Answer "No Information" if:**
- Insufficient description of outcome measures
- Cannot determine objectivity or subjectivity of outcomes
- Unclear potential for influence by knowledge

**Consider outcome types:** Mortality (objective), laboratory measurements (objective), imaging with independent blinded assessment (objective), clinical diagnoses requiring judgment (potentially subjective), symptom scales (subjective), patient-reported outcomes (subjective)"""
                    },
                    {
                        "id": "6.2",
                        "text": "Were outcome assessors blinded to exposure status?",
                        "guidance": """Look for information about whether those assessing outcomes were unaware of participants' exposure status.

**Answer "Yes" if:**
- Explicit statement of blinded outcome assessment
- Clear procedures ensuring assessors unaware of exposure
- Outcomes assessed independently from exposure information
- Objective outcomes from systems/registries without assessor involvement

**Answer "Probably Yes" if:**
- Some blinding procedures described but incomplete details
- Administrative separation likely preventing exposure knowledge
- Processes suggesting independent assessment

**Answer "No" if:**
- Explicit statement that assessors were aware of exposure status
- Unblinded assessment of subjective outcomes
- Study design necessarily revealing exposure to assessors
- Self-reported outcomes with participant knowledge of exposure

**Answer "Probably No" if:**
- Limited blinding with potential for exposure information to be known
- Procedures suggesting most assessors could determine exposure status
- Inadequate safeguards against unblinding

**Answer "No Information" if:**
- No mention of blinding for outcome assessment
- Cannot determine if assessors knew exposure status
- Unclear procedures for outcome determination

**Look for:** Blinding procedures, masked assessment, independent outcome committees, separation of staff assessing outcomes from those managing exposures, data collection methods preventing exposure disclosure"""
                    },
                    {
                        "id": "6.3",
                        "text": "Were the methods of outcome assessment comparable between groups?",
                        "guidance": """Look for information about whether outcome assessment methods were consistent across exposure groups.

**Answer "Yes" if:**
- Identical outcome assessment methods for all exposure groups
- Standardized protocols applied uniformly regardless of exposure
- Same data sources used for all participants
- Equal surveillance intensity across groups

**Answer "Probably Yes" if:**
- Generally consistent methods with minor variations unlikely to bias
- Mostly standardized approaches across groups
- Similar assessment procedures for key outcomes

**Answer "No" if:**
- Different outcome assessment methods between exposure groups
- Varying surveillance intensity by exposure status
- Different data sources or definitions by group
- Systematic differences in assessment procedures

**Answer "Probably No" if:**
- Some concerning differences in assessment methods
- Potential for differential ascertainment between groups
- Inconsistent procedures that could affect results

**Answer "No Information" if:**
- Insufficient detail about outcome assessment methods
- Cannot determine consistency across exposure groups
- Unclear procedures for outcome determination

**Examples of differential assessment:** Different follow-up schedules, different diagnostic criteria, different data sources, variable intensity of surveillance, different assessment tools or questionnaires"""
                    },
                    {
                        "id": "6.4",
                        "text": "Could differences in outcome assessment have affected results?",
                        "guidance": """Look for information about whether any differences in outcome assessment between groups could have meaningfully impacted results.

**Answer "Yes" if:**
- Assessment differences directly related to outcomes of interest
- Magnitude of differential assessment likely to substantially affect results
- Pattern of results consistent with assessment bias
- Different methods with known varying sensitivity/specificity

**Answer "Probably Yes" if:**
- Assessment differences possibly affecting results
- Some evidence suggesting impact on outcome detection
- Potential for meaningful effect on findings

**Answer "No" if:**
- Assessment differences unrelated to key outcomes
- Sensitivity analyses showing robustness to assessment variations
- Differences too minor to meaningfully impact results
- Strong design features preventing assessment differences from affecting results

**Answer "Probably No" if:**
- Limited potential impact of any assessment differences
- Minor variations unlikely to substantially affect findings
- Mostly consistent assessment for critical outcomes

**Answer "No Information" if:**
- Cannot determine impact of any assessment differences
- Insufficient information about assessment methods
- Unclear potential for bias from assessment variations

**Consider:** Magnitude of assessment differences, relationship to specific outcomes, potential direction of bias, sensitivity analyses addressing assessment variation, objective vs. subjective components"""
                    }
                ]
            },
            "domain_7": {
                "title": "Domain 7: Risk of bias in selection of the reported result",
                "description": "This domain addresses whether results were selectively reported based on findings or whether analyses were pre-specified.",
                "questions": [
                    {
                        "id": "7.1",
                        "text": "Were the data analyses in accordance with a pre-specified plan?",
                        "guidance": """Look for information about whether analyses were planned before examining the data.

**Answer "Yes" if:**
- Reference to published protocol with detailed analysis plan
- Registration record with pre-specified analyses
- Clear statement of a priori analytical approach
- Statistical analysis plan finalized before data analysis

**Answer "Probably Yes" if:**
- Some evidence suggesting pre-specified analyses
- Reference to protocol without full details
- Standard analytical approach typical for the field
- Mostly consistent with typical pre-planned methods

**Answer "No" if:**
- Explicit statement of post-hoc or exploratory analyses without distinction from main analyses
- Clear evidence of data-driven analytical decisions
- Multiple analytical approaches without pre-specification
- Analysis plan evidently modified after seeing results

**Answer "Probably No" if:**
- Limited evidence of pre-specification
- Some analytical choices appearing data-driven
- Selective analytical approaches suggesting potential fishing

**Answer "No Information" if:**
- No mention of analysis planning or timing
- Cannot determine if analyses were pre-specified
- No reference to protocols or analysis plans

**Look for:** References to protocols or statistical analysis plans, clinical trial registration with analysis details, statements about a priori hypotheses, distinction between planned and post-hoc analyses"""
                    },
                    {
                        "id": "7.2",
                        "text": "Were there multiple outcome measurements or analysis methods from which results could be chosen?",
                        "guidance": """Look for information about whether multiple outcome definitions, time points, or analytical approaches were available.

**Answer "Yes" if:**
- Multiple outcome measures or definitions explicitly mentioned
- Various time points measured without clear primary specification
- Multiple analytical approaches described for same research question
- Composite outcomes with multiple possible combinations
- Various subgroups or stratifications examined

**Answer "Probably Yes" if:**
- Some indication of multiple measures or approaches
- Potential for selective reporting based on methods description
- Likely multiple analyses without comprehensive reporting

**Answer "No" if:**
- Single clear pre-specified outcome measure and analysis approach
- Comprehensive reporting of all measured outcomes
- Clear primary outcome with transparent secondary analyses
- Complete results for all mentioned measures and methods

**Answer "Probably No" if:**
- Limited opportunities for selection from multiple analyses
- Generally transparent reporting of measured outcomes
- Mostly comprehensive results presentation

**Answer "No Information" if:**
- Cannot determine what outcomes were measured
- Unclear analytical approaches used
- Insufficient reporting of methods to assess multiplicity

**Look for:** Multiple scales or definitions, various time points, alternative analytical approaches, subgroup analyses, adjusted and unadjusted results, composite outcomes, competing modeling strategies"""
                    },
                    {
                        "id": "7.3",
                        "text": "Was the study free from selective reporting of results based on the findings?",
                        "guidance": """Look for information about whether there is evidence of selective reporting of particular results.

**Answer "Yes" if:**
- Comprehensive reporting of all pre-specified analyses
- Results for all mentioned outcomes provided
- Non-significant findings presented with same detail as significant ones
- Consistent with registered protocol if available

**Answer "Probably Yes" if:**
- Generally complete reporting with minor limitations
- Most expected results presented regardless of significance
- No strong indication of selective reporting

**Answer "No" if:**
- Clear discrepancies between planned and reported analyses
- Results missing for mentioned outcomes
- Emphasis on significant findings with minimal detail for non-significant results
- Inconsistent with registered protocol or prior publications
- Post-hoc analyses presented as main findings without clear labeling

**Answer "Probably No" if:**
- Some evidence suggesting selective reporting
- Incomplete results for certain outcomes or analyses
- Pattern of reporting favoring significant or positive findings

**Answer "No Information" if:**
- Cannot determine completeness of reporting
- No protocol or registration to compare against
- Insufficient information about planned analyses

**Look for:** Comparison with protocols or registrations, comprehensive reporting of outcomes listed in methods, balanced presentation of significant and non-significant results, justification for any changes from planned analyses"""
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
Please conduct a complete Risk of Bias assessment for this non-randomized study of exposure using the ROBINS-E tool. You will assess all seven domains systematically.

For each signalling question:
1. Provide your answer using EXACTLY one of: "Yes", "Probably Yes", "Probably No", "No", or "No Information"  
2. Provide a brief justification with specific quotes or references from the article
3. If no relevant information is found, answer "No Information"

Please format your response as JSON with the following structure:
```json
{{
    "domain_1": {{
        "1.1": {{"answer": "Yes/PY/PN/No/NI", "justification": "..."}},
        "1.2": {{"answer": "Yes/PY/PN/No/NI", "justification": "..."}},
        ...
    }},
    "domain_2": {{
        "2.1": {{"answer": "Yes/PY/PN/No/NI", "justification": "..."}},
        ...
    }},
    ...
}}
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

**Confounding Content:**
{chr(10).join(extracted_content.get('confounding', []))}

**Exposure Measurement Content:** 
{chr(10).join(extracted_content.get('exposure_measurement', []))}

**Selection Content:**
{chr(10).join(extracted_content.get('selection', []))}

**Post-exposure Interventions Content:**
{chr(10).join(extracted_content.get('post_exposure_interventions', []))}

**Missing Data Content:**
{chr(10).join(extracted_content.get('missing_data', []))}

**Outcome Measurement Content:**
{chr(10).join(extracted_content.get('outcome_measurement', []))}

**Selective Reporting Content:**
{chr(10).join(extracted_content.get('selective_reporting', []))}

## FULL ARTICLE TEXT:
{study_text}

## ASSESSMENT TASK:
Based on the extracted content above and the full article text, please provide a complete ROBINS-E assessment. The extracted content highlights potentially relevant sentences, but you should also consider the full article context.

Please respond in JSON format with your assessment for all signalling questions across the 7 domains.

```json
{
    "domain_1": {
        "1.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "1.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "1.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "1.4": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "1.5": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    },
    "domain_2": {
        "2.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "2.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "2.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    },
    "domain_3": {
        "3.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "3.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "3.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    },
    "domain_4": {
        "4.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "4.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "4.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    },
    "domain_5": {
        "5.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "5.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "5.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "5.4": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    },
    "domain_6": {
        "6.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "6.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "6.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "6.4": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    },
    "domain_7": {
        "7.1": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "7.2": {"answer": "Yes/PY/PN/No/NI", "justification": "..."},
        "7.3": {"answer": "Yes/PY/PN/No/NI", "justification": "..."}
    }
}
```
"""
        return prompt
