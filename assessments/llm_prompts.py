"""
Comprehensive LLM Prompts for RoB 2.0 Parallel Trial Assessments

This module contains detailed, precise prompts designed to guide LLMs
in making accurate risk of bias assessments following the RoB 2.0 methodology.
"""

ROB2_SYSTEM_PROMPT = """
You are an expert systematic reviewer and methodologist specializing in the Cochrane Risk of Bias 2.0 (RoB 2) tool for parallel randomized controlled trials. Your task is to conduct rigorous, evidence-based risk of bias assessments.

Key principles:
1. Follow the official RoB 2.0 methodology exactly as specified by Cochrane
2. Base assessments solely on information provided in study documents
3. Use conservative judgments when information is unclear or missing
4. Provide detailed, scientific reasoning for each assessment
5. Be consistent in applying criteria across all domains
6. Focus on the specific outcome being assessed

Response format requirements:
- Provide responses in valid JSON format
- Include confidence scores (0-1) for each assessment
- Cite specific text from documents when available
- Follow the exact RoB 2.0 signaling questions and decision rules
"""

ROB2_ASSESSMENT_PROMPT = """
Conduct a comprehensive Risk of Bias 2.0 assessment for the following parallel randomized controlled trial. 

{study_context}

ASSESSMENT INSTRUCTIONS:

You must assess each of the 5 domains of RoB 2.0 for parallel trials:

**DOMAIN 1: Bias arising from the randomization process**
Signaling Questions:
1.1: Was the allocation sequence random? (Y/PY/PN/N/NI)
1.2: Was the allocation sequence concealed until participants were enrolled and assigned to interventions? (Y/PY/PN/N/NI)  
1.3: Did baseline differences between intervention groups suggest a problem with the randomization process? (Y/PY/PN/N/NI)

Assessment criteria:
- LOW RISK: Adequate concealment AND no concerning baseline imbalances AND random sequence
- HIGH RISK: Inadequate concealment OR baseline imbalances suggest randomization problems
- SOME CONCERNS: All other scenarios

**DOMAIN 2: Bias due to deviations from intended interventions (effect of assignment to intervention)**
Signaling Questions:
2.1: Were participants aware of their assigned intervention during the trial? (Y/PY/PN/N/NI)
2.2: Were carers and people delivering the interventions aware of participants' assigned intervention during the trial? (Y/PY/PN/N/NI)
2.3: If Y/PY to 2.1 or 2.2: Were there deviations from the intended intervention that arose because of the trial context? (Y/PY/PN/N/NI/NA)
2.4: If Y/PY to 2.3: Were these deviations likely to have affected the outcome? (Y/PY/PN/N/NI/NA)
2.5: If Y/PY to 2.4: Were these deviations balanced between groups? (Y/PY/PN/N/NI/NA)
2.6: Was an appropriate analysis used to estimate the effect of assignment to intervention? (Y/PY/PN/N/NI)
2.7: If N/PN/NI to 2.6: Was there substantial impact on the result due to failure to analyse participants in the group to which they were randomized? (Y/PY/PN/N/NI/NA)

Assessment criteria:
- LOW RISK: (Both participants and personnel unaware) OR (aware but no deviations) AND appropriate analysis
- HIGH RISK: Unbalanced outcome-affecting deviations OR inappropriate analysis with substantial impact
- SOME CONCERNS: All other scenarios

**DOMAIN 3: Bias due to missing outcome data**
Signaling Questions:
3.1: Were outcome data available for all, or nearly all, randomized participants? (Y/PY/PN/N/NI)
3.2: If N/PN/NI to 3.1: Is there evidence that the result was not biased by missing outcome data? (Y/PY/PN/N/NI/NA)
3.3: If N/PN to 3.2: Could missingness in the outcome depend on its true value? (Y/PY/PN/N/NI/NA)
3.4: If Y/PY/NI to 3.3: Is it likely that missingness in the outcome depended on its true value? (Y/PY/PN/N/NI/NA)

Assessment criteria:
- LOW RISK: Complete data OR evidence of no bias OR missingness cannot depend on true value
- HIGH RISK: Incomplete data AND no evidence of no bias AND missingness likely depends on true value
- SOME CONCERNS: All other scenarios

**DOMAIN 4: Bias in measurement of the outcome**  
Signaling Questions:
4.1: Was the method of measuring the outcome inappropriate? (Y/PY/PN/N/NI)
4.2: If N/PN/NI to 4.1: Could measurement or ascertainment of the outcome have differed between intervention groups? (Y/PY/PN/N/NI/NA)
4.3: If N/PN/NI to 4.2: Were outcome assessors aware of the intervention received by study participants? (Y/PY/PN/N/NI/NA)
4.4: If Y/PY/NI to 4.3: Could assessment of the outcome have been influenced by knowledge of intervention received? (Y/PY/PN/N/NI/NA)
4.5: If Y/PY/NI to 4.4: Is it likely that assessment of the outcome was influenced by knowledge of intervention received? (Y/PY/PN/N/NI/NA)

Assessment criteria:
- LOW RISK: Appropriate method AND consistent measurement AND (blinded assessors OR cannot be influenced)
- HIGH RISK: Inappropriate method OR differential measurement OR likely influenced by knowledge
- SOME CONCERNS: All other scenarios

**DOMAIN 5: Bias in selection of the reported result**
Signaling Questions:
5.1: Were the data that produced this result analysed in accordance with a pre-specified plan that was finalized before unblinded outcome data were available for analysis? (Y/PY/PN/N/NI)
5.2: Is the numerical result being assessed likely to have been selected, on the basis of the results, from multiple eligible outcome measurements (e.g., scales, definitions, time points) within the outcome domain? (Y/PY/PN/N/NI)
5.3: Is the numerical result being assessed likely to have been selected, on the basis of the results, from multiple eligible analyses of the data? (Y/PY/PN/N/NI)

Assessment criteria:
- LOW RISK: Pre-specified plan AND no selection from multiple outcomes/analyses
- HIGH RISK: Result likely selected from multiple outcomes OR analyses based on results
- SOME CONCERNS: All other scenarios

**OVERALL ASSESSMENT:**
- LOW RISK: All domains low risk
- HIGH RISK: Any domain high risk OR 3+ domains with some concerns  
- SOME CONCERNS: 1-2 domains with some concerns, no high risk

REQUIRED OUTPUT FORMAT:
Provide your assessment in the following JSON structure:

```json
{
  "domain_1": {
    "questions": {
      "1.1": {"response": "Y/PY/PN/N/NI", "justification": "Detailed reasoning with citations"},
      "1.2": {"response": "Y/PY/PN/N/NI", "justification": "Detailed reasoning with citations"},
      "1.3": {"response": "Y/PY/PN/N/NI", "justification": "Detailed reasoning with citations"}
    },
    "risk_assessment": "Low/Some concerns/High",
    "reasoning": "Detailed explanation of domain assessment",
    "confidence": 0.0-1.0,
    "key_evidence": ["Quote 1", "Quote 2"]
  },
  "domain_2": {
    "questions": {
      "2.1": {"response": "Y/PY/PN/N/NI", "justification": "Detailed reasoning"},
      "2.2": {"response": "Y/PY/PN/N/NI", "justification": "Detailed reasoning"},
      "2.3": {"response": "Y/PY/PN/N/NI/NA", "justification": "Detailed reasoning"},
      "2.4": {"response": "Y/PY/PN/N/NI/NA", "justification": "Detailed reasoning"},
      "2.5": {"response": "Y/PY/PN/N/NI/NA", "justification": "Detailed reasoning"},
      "2.6": {"response": "Y/PY/PN/N/NI", "justification": "Detailed reasoning"},
      "2.7": {"response": "Y/PY/PN/N/NI/NA", "justification": "Detailed reasoning"}
    },
    "risk_assessment": "Low/Some concerns/High",
    "reasoning": "Detailed explanation of domain assessment",
    "confidence": 0.0-1.0,
    "key_evidence": ["Quote 1", "Quote 2"]
  },
  "domain_3": {
    "questions": {
      "3.1": {"response": "Y/PY/PN/N/NI", "justification": "Detailed reasoning"},
      "3.2": {"response": "Y/PY/PN/N/NI/NA", "justification": "Detailed reasoning"},
      "3.3": {"response": "Y/PY/PN/N/NI/NA", "justification": "Detailed reasoning"},
      "3.4": {"response": "Y/PY/PN/N/NI/NA", "justification": "Detailed reasoning"}
    },
    "risk_assessment": "Low/Some concerns/High",
    "reasoning": "Detailed explanation of domain assessment",
    "confidence": 0.0-1.0,
    "key_evidence": ["Quote 1", "Quote 2"]
  },
  "domain_4": {
    "questions": {
      "4.1": {"response": "Y/PY/PN/N/NI", "justification": "Detailed reasoning"},
      "4.2": {"response": "Y/PY/PN/N/NI/NA", "justification": "Detailed reasoning"},
      "4.3": {"response": "Y/PY/PN/N/NI/NA", "justification": "Detailed reasoning"},
      "4.4": {"response": "Y/PY/PN/N/NI/NA", "justification": "Detailed reasoning"},
      "4.5": {"response": "Y/PY/PN/N/NI/NA", "justification": "Detailed reasoning"}
    },
    "risk_assessment": "Low/Some concerns/High",
    "reasoning": "Detailed explanation of domain assessment",
    "confidence": 0.0-1.0,
    "key_evidence": ["Quote 1", "Quote 2"]
  },
  "domain_5": {
    "questions": {
      "5.1": {"response": "Y/PY/PN/N/NI", "justification": "Detailed reasoning"},
      "5.2": {"response": "Y/PY/PN/N/NI", "justification": "Detailed reasoning"},
      "5.3": {"response": "Y/PY/PN/N/NI", "justification": "Detailed reasoning"}
    },
    "risk_assessment": "Low/Some concerns/High",
    "reasoning": "Detailed explanation of domain assessment",
    "confidence": 0.0-1.0,
    "key_evidence": ["Quote 1", "Quote 2"]
  },
  "overall": {
    "risk_assessment": "Low/Some concerns/High",
    "reasoning": "Detailed explanation of overall assessment logic",
    "confidence": 0.0-1.0,
    "summary": "Brief summary of key bias concerns",
    "recommendations": ["Recommendation 1", "Recommendation 2"]
  },
  "meta": {
    "assessment_date": "ISO date",
    "outcome_assessed": "Primary outcome name",
    "documents_used": ["Document 1", "Document 2"],
    "limitations": ["Limitation 1", "Limitation 2"]
  }
}
```

CRITICAL INSTRUCTIONS:
1. Answer ALL signaling questions based strictly on information in the provided documents
2. Use "No Information" (NI) conservatively only when truly no relevant information exists
3. Provide specific quotes from documents as evidence whenever possible
4. Follow the conditional logic (e.g., skip questions if previous answers are N/PN)
5. Ensure your domain risk assessments follow the exact RoB 2.0 decision algorithms
6. Your overall assessment MUST follow the combination rules (High if any domain High, etc.)
7. Include confidence scores reflecting certainty in available evidence
8. Be thorough but focus on the most relevant evidence for each question

Begin your assessment now:
"""

def get_domain_specific_prompt(domain_number: int, study_context: str) -> str:
    """Get a focused prompt for assessing a specific domain"""
    
    domain_prompts = {
        1: f"""
Assess Domain 1 (Randomization Process) for this study:

{study_context}

Focus specifically on:
- How randomization sequence was generated
- Whether allocation was concealed until assignment
- Baseline characteristics and any imbalances
- Any evidence of selection bias

Provide detailed assessment following RoB 2.0 methodology for Domain 1 only.
""",
        
        2: f"""
Assess Domain 2 (Deviations from Intended Interventions) for this study:

{study_context}

Focus specifically on:
- Participant and personnel blinding status
- Any deviations from protocol and their causes
- Whether deviations affected outcomes
- Balance of deviations between groups
- Analysis method (ITT vs per-protocol)

Provide detailed assessment following RoB 2.0 methodology for Domain 2 only.
""",
        
        3: f"""
Assess Domain 3 (Missing Outcome Data) for this study:

{study_context}

Focus specifically on:
- Completeness of outcome data
- Reasons for missing data
- Differential missingness between groups
- Impact of missing data on results
- Any sensitivity analyses performed

Provide detailed assessment following RoB 2.0 methodology for Domain 3 only.
""",
        
        4: f"""
Assess Domain 4 (Outcome Measurement) for this study:

{study_context}

Focus specifically on:
- Appropriateness of outcome measurement method
- Consistency of measurement between groups
- Blinding of outcome assessors
- Potential for measurement bias
- Objectivity vs subjectivity of outcome

Provide detailed assessment following RoB 2.0 methodology for Domain 4 only.
""",
        
        5: f"""
Assess Domain 5 (Selective Reporting) for this study:

{study_context}

Focus specifically on:
- Pre-specified analysis plan and timing
- Multiple outcome measurements or time points
- Multiple analysis methods
- Evidence of selective reporting
- Protocol vs publication consistency

Provide detailed assessment following RoB 2.0 methodology for Domain 5 only.
"""
    }
    
    return domain_prompts.get(domain_number, "Invalid domain number")

def get_validation_prompt(assessment_json: str) -> str:
    """Prompt to validate and refine an assessment"""
    return f"""
Review and validate this RoB 2.0 assessment for accuracy and completeness:

{assessment_json}

Check for:
1. Logical consistency between signaling question responses and domain risk ratings
2. Proper application of RoB 2.0 decision algorithms  
3. Appropriate use of conditional questions (NA when conditions not met)
4. Overall risk rating follows combination rules correctly
5. Evidence citations support the judgments made
6. All required fields are completed

Provide the corrected assessment in the same JSON format, with explanations for any changes made.
"""

def get_confidence_calibration_prompt() -> str:
    """Prompt to help calibrate confidence scores"""
    return """
When assigning confidence scores (0-1), use these guidelines:

0.9-1.0: Clear, explicit evidence directly addresses the question
0.7-0.8: Strong evidence with minor ambiguity or inference required  
0.5-0.6: Moderate evidence requiring substantial inference
0.3-0.4: Weak or indirect evidence, high uncertainty
0.1-0.2: Very little relevant information, mostly speculation
0.0: No relevant information available

Consider:
- Explicitness of reported information
- Quality and detail of methodology description  
- Consistency of information across documents
- Potential for multiple interpretations
- Missing information that would be expected
"""
