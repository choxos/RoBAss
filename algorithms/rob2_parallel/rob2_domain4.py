def assess_outcome_measurement_bias(q4_1_method_inappropriate, q4_2_differ_between_groups,
                                   q4_3_assessors_aware, q4_4_could_be_influenced, 
                                   q4_5_likely_influenced):
    """
    RoB 2 Domain 4: Risk of bias in measurement of the outcome
    
    Parameters:
    q4_1_method_inappropriate (str): Was the method of measuring the outcome inappropriate?
    q4_2_differ_between_groups (str): Could measurement or ascertainment of the outcome have differed between intervention groups?
    q4_3_assessors_aware (str): Were outcome assessors aware of the intervention received by study participants?
    q4_4_could_be_influenced (str): If Y/PY to 4.3: Could assessment of the outcome have been influenced by knowledge of intervention?
    q4_5_likely_influenced (str): If Y/PY to 4.4: Is it likely that assessment of the outcome was influenced by knowledge of intervention?
    
    Response options: 'Y', 'PY', 'PN', 'N', 'NI', 'NA'
    
    Returns:
    tuple: (risk_level, reasoning)
    """
    
    # Normalize inputs
    q4_1 = q4_1_method_inappropriate.upper()
    q4_2 = q4_2_differ_between_groups.upper()
    q4_3 = q4_3_assessors_aware.upper()
    q4_4 = q4_4_could_be_influenced.upper()
    q4_5 = q4_5_likely_influenced.upper()
    
    # Validate inputs
    valid_responses = ['Y', 'PY', 'PN', 'N', 'NI', 'NA']
    if not all(inp in valid_responses for inp in [q4_1, q4_2, q4_3, q4_4, q4_5]):
        raise ValueError("Invalid response. Use: Y, PY, PN, N, NI, or NA")
    
    # HIGH RISK criteria (any one of these conditions):
    # (i) The method of measuring the outcome was inappropriate
    if q4_1 in ['Y', 'PY']:
        return ('High', 'Inappropriate method of measuring the outcome')
    
    # (ii) The measurement or ascertainment of the outcome could have differed between intervention groups
    if q4_2 in ['Y', 'PY']:
        return ('High', 'Measurement or ascertainment of outcome differed between intervention groups')
    
    # (iii) It is likely that assessment of the outcome was influenced by knowledge of the intervention received
    if (q4_3 in ['Y', 'PY', 'NI'] and 
        q4_4 in ['Y', 'PY', 'NI'] and 
        q4_5 in ['Y', 'PY', 'NI']):
        return ('High', 'Assessment likely influenced by knowledge of intervention assignment')
    
    # LOW RISK criteria (all conditions must be met):
    # (i) The method of measuring the outcome was not inappropriate
    # AND (ii) The measurement or ascertainment of the outcome did not differ between intervention groups
    # AND (iii.1) The outcome assessors were unaware of the intervention received
    # OR (iii.2) The assessment could not have been influenced by knowledge of intervention
    
    method_appropriate = q4_1 in ['N', 'PN', 'NI']
    measurement_consistent = q4_2 in ['N', 'PN']
    assessors_blinded = q4_3 in ['N', 'PN']
    cannot_be_influenced = (q4_3 in ['Y', 'PY', 'NI'] and q4_4 in ['N', 'PN'])
    
    if method_appropriate and measurement_consistent and (assessors_blinded or cannot_be_influenced):
        if assessors_blinded:
            return ('Low', 'Appropriate measurement method, consistent between groups, and assessors blinded')
        else:
            return ('Low', 'Appropriate measurement method, consistent between groups, and assessment cannot be influenced by knowledge')
    
    # SOME CONCERNS criteria:
    # Scenario 1: Appropriate method, consistent measurement, but potential for bias that is unlikely
    if (method_appropriate and measurement_consistent and 
        q4_3 in ['Y', 'PY', 'NI'] and q4_4 in ['Y', 'PY', 'NI'] and q4_5 in ['N', 'PN']):
        return ('Some concerns', 'Potential for assessment bias exists but unlikely to have influenced results')
    
    # Scenario 2: Appropriate method, no information about differential measurement, but assessors blinded or cannot be influenced
    if (method_appropriate and q4_2 == 'NI' and (assessors_blinded or cannot_be_influenced)):
        if assessors_blinded:
            return ('Some concerns', 'No information about differential measurement, but assessors were blinded')
        else:
            return ('Some concerns', 'No information about differential measurement, but assessment cannot be influenced')
    
    # Handle remaining scenarios
    if method_appropriate and q4_2 == 'NI':
        return ('Some concerns', 'No information about whether measurement differed between groups')
    
    # Default fallback for edge cases
    return ('Some concerns', 'Intermediate scenario with some potential for measurement bias')


def detailed_assessment_domain4(q4_1, q4_2, q4_3, q4_4, q4_5, study_info="",
                               outcome_type=None, measurement_method=None, 
                               blinding_description=None):
    """
    Provides detailed assessment with contextual information
    
    Additional parameters:
    outcome_type (str): Type of outcome (e.g., "objective", "subjective", "patient-reported")
    measurement_method (str): Description of measurement method
    blinding_description (str): Details about outcome assessor blinding
    """
    risk, reasoning = assess_outcome_measurement_bias(q4_1, q4_2, q4_3, q4_4, q4_5)
    
    print("=== RoB 2 Domain 4: Bias in measurement of the outcome ===")
    if study_info:
        print(f"Study: {study_info}")
    if outcome_type:
        print(f"Outcome type: {outcome_type}")
    if measurement_method:
        print(f"Measurement method: {measurement_method}")
    if blinding_description:
        print(f"Assessor blinding: {blinding_description}")
    print()
    
    print("Signaling Questions:")
    print(f"4.1 Was the method of measuring the outcome inappropriate? {q4_1}")
    
    # Conditional questions based on flowchart logic
    if q4_1 in ['N', 'PN', 'NI']:
        print(f"4.2 Could measurement/ascertainment differ between groups? {q4_2}")
        
        if q4_2 in ['N', 'PN', 'NI']:  # Continue if not clearly different
            print(f"4.3 Were outcome assessors aware of intervention received? {q4_3}")
            
            if q4_3 in ['Y', 'PY', 'NI']:
                print(f"4.4 Could assessment have been influenced by knowledge of intervention? {q4_4}")
                
                if q4_4 in ['Y', 'PY', 'NI']:
                    print(f"4.5 Is it likely that assessment was influenced by knowledge? {q4_5}")
    
    print()
    print(f"Risk Assessment: {risk}")
    print(f"Reasoning: {reasoning}")
    print()
    
    # Additional guidance based on risk level and outcome characteristics
    if risk == "Low":
        print("✓ This domain poses low risk of bias")
        print("Outcome measurement appears robust and unbiased")
        
    elif risk == "Some concerns":
        print("⚠ This domain raises some concerns about potential measurement bias")
        print("Considerations:")
        
        if outcome_type and "subjective" in outcome_type.lower():
            print("- Subjective outcomes are more susceptible to assessment bias")
        if q4_3 in ['Y', 'PY', 'NI']:
            print("- Lack of assessor blinding increases potential for bias")
        if q4_2 == 'NI':
            print("- Unclear whether measurement procedures were standardized between groups")
            
        print("Recommendations:")
        print("- Consider whether bias could plausibly affect results")
        print("- Assess if outcome measurement was standardized")
        
    else:  # High risk
        print("⚠ This domain poses high risk of bias")
        print("Critical measurement issues identified:")
        
        if q4_1 in ['Y', 'PY']:
            print("- Inappropriate measurement method used")
        if q4_2 in ['Y', 'PY']:
            print("- Measurement differed between intervention groups")
        if q4_5 in ['Y', 'PY', 'NI']:
            print("- Assessment likely biased by knowledge of intervention")
            
        print("- Results should be interpreted with significant caution")
        print("- Consider whether measurement bias could explain observed effects")
    
    return risk, reasoning


def classify_outcome_susceptibility(outcome_description):
    """
    Helper function to classify outcome susceptibility to measurement bias
    """
    outcome_lower = outcome_description.lower()
    
    # Objective outcomes (low susceptibility)
    objective_keywords = ['mortality', 'death', 'laboratory', 'biomarker', 'imaging', 
                         'vital signs', 'blood pressure', 'weight', 'height', 'bmi']
    
    # Subjective outcomes (high susceptibility)  
    subjective_keywords = ['pain', 'quality of life', 'depression', 'anxiety', 'satisfaction',
                          'patient-reported', 'questionnaire', 'scale', 'rating', 'symptom']
    
    # Semi-objective outcomes (moderate susceptibility)
    semi_objective_keywords = ['clinical assessment', 'physician rating', 'functional test',
                              'performance', 'adherence', 'compliance']
    
    if any(keyword in outcome_lower for keyword in objective_keywords):
        return "Objective (low susceptibility to bias)"
    elif any(keyword in outcome_lower for keyword in subjective_keywords):
        return "Subjective (high susceptibility to bias)"
    elif any(keyword in outcome_lower for keyword in semi_objective_keywords):
        return "Semi-objective (moderate susceptibility to bias)"
    else:
        return "Classification unclear"


# Example usage and test cases
if __name__ == "__main__":
    print("Testing RoB 2 Domain 4 Assessment Algorithm\n")
    
    # Test case 1: Low risk - objective outcome, blinded assessors
    print("Test 1 - Low Risk (Objective outcome, blinded assessors):")
    detailed_assessment_domain4('N', 'N', 'N', 'NA', 'NA',
                              "RCT of blood pressure medication",
                              outcome_type="Objective",
                              measurement_method="Automated blood pressure monitor",
                              blinding_description="Research nurses blinded to treatment assignment")
    print("-" * 80)
    
    # Test case 2: Low risk - subjective outcome but cannot be influenced
    print("Test 2 - Low Risk (Assessment cannot be influenced):")
    detailed_assessment_domain4('N', 'N', 'Y', 'N', 'NA',
                              "RCT with standardized questionnaire",
                              outcome_type="Patient-reported",
                              measurement_method="Validated depression scale (self-administered)",
                              blinding_description="Participants aware, but self-administered scale")
    print("-" * 80)
    
    # Test case 3: Some concerns - potential bias but unlikely
    print("Test 3 - Some Concerns (Potential bias but unlikely):")
    detailed_assessment_domain4('N', 'N', 'Y', 'PY', 'N',
                              "RCT with clinical assessment",
                              outcome_type="Semi-objective",
                              measurement_method="Standardized functional assessment",
                              blinding_description="Unblinded clinicians using standardized protocol")
    print("-" * 80)
    
    # Test case 4: High risk - inappropriate method
    print("Test 4 - High Risk (Inappropriate measurement method):")
    detailed_assessment_domain4('Y', 'NA', 'NA', 'NA', 'NA',
                              "Study with unreliable outcome measure",
                              outcome_type="Subjective",
                              measurement_method="Non-validated, single-item scale")
    print("-" * 80)
    
    # Test case 5: High risk - differential measurement
    print("Test 5 - High Risk (Differential measurement between groups):")
    detailed_assessment_domain4('N', 'Y', 'NA', 'NA', 'NA',
                              "Study with different assessment protocols",
                              measurement_method="Different follow-up schedules by group")
    print("-" * 80)
    
    # Test case 6: High risk - likely influenced by knowledge
    print("Test 6 - High Risk (Assessment likely influenced):")
    detailed_assessment_domain4('N', 'N', 'Y', 'Y', 'Y',
                              "Open-label trial with subjective endpoint",
                              outcome_type="Subjective",
                              measurement_method="Physician global assessment",
                              blinding_description="Unblinded investigators rating improvement")
    print("-" * 80)
    
    # Test outcome classification
    print("Test 7 - Outcome Susceptibility Classification:")
    outcomes = [
        "All-cause mortality at 12 months",
        "Patient-reported pain on 0-10 scale", 
        "Blood pressure measured by automated device",
        "Physician assessment of clinical improvement",
        "Hospital readmission within 30 days"
    ]
    
    for outcome in outcomes:
        classification = classify_outcome_susceptibility(outcome)
        print(f"'{outcome}' → {classification}")
