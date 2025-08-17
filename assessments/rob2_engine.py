"""
RoB 2.0 Assessment Engine for Parallel Randomized Controlled Trials

This module implements the complete RoB 2.0 assessment algorithms based on the
official Cochrane methodology for parallel group trials.
"""

def assess_domain_1_randomization(q1_sequence_random, q2_allocation_concealed, q3_baseline_imbalance):
    """
    Domain 1: Risk of bias arising from the randomization process
    """
    # Normalize inputs to uppercase
    q1 = q1_sequence_random.upper()
    q2 = q2_allocation_concealed.upper()
    q3 = q3_baseline_imbalance.upper()
    
    # Validate inputs
    valid_responses = ['Y', 'PY', 'PN', 'N', 'NI']
    if q1 not in valid_responses or q2 not in valid_responses or q3 not in valid_responses:
        raise ValueError("Invalid response. Use: Y, PY, PN, N, or NI")
    
    # LOW RISK criteria
    if (q2 in ['Y', 'PY'] and  # Allocation sequence adequately concealed
        q3 in ['N', 'PN', 'NI'] and  # No concerning baseline imbalances
        q1 in ['Y', 'PY', 'NI']):  # Sequence was random or no info
        return ('Low', 'Allocation sequence adequately concealed, no concerning baseline imbalances, and randomization appropriate')
    
    # HIGH RISK criteria
    if (q2 in ['N', 'PN'] or  # Allocation sequence not adequately concealed
        (q2 == 'NI' and q3 in ['Y', 'PY'])):  # No info on concealment AND baseline imbalances suggest problem
        return ('High', 'Allocation sequence not adequately concealed or baseline imbalances suggest randomization problems')
    
    # Additional HIGH RISK: Any response to sequence generation that is N/PN with baseline imbalances
    if q1 in ['N', 'PN'] and q3 in ['Y', 'PY']:
        return ('High', 'Non-random sequence generation with baseline imbalances suggesting problems')
    
    # SOME CONCERNS - all other combinations
    reasoning_parts = []
    if q1 in ['N', 'PN']:
        reasoning_parts.append("non-random or probably non-random sequence generation")
    if q2 == 'NI':
        reasoning_parts.append("no information about allocation concealment")
    if q3 in ['Y', 'PY']:
        reasoning_parts.append("baseline imbalances suggest potential problems")
    
    if reasoning_parts:
        reasoning = "Some concerns due to: " + ", ".join(reasoning_parts)
    else:
        reasoning = "Some concerns - intermediate risk scenario not meeting low or high risk criteria"
    
    return ('Some concerns', reasoning)


def assess_domain_2_deviations(q2_1_participants_aware, q2_2_personnel_aware, q2_3_deviations_occurred,
                              q2_4_deviations_affect_outcome, q2_5_deviations_balanced,
                              q2_6_appropriate_analysis, q2_7_substantial_impact):
    """
    Domain 2: Risk of bias due to deviations from intended interventions
    """
    # Normalize inputs
    inputs = [q2_1_participants_aware, q2_2_personnel_aware, q2_3_deviations_occurred,
              q2_4_deviations_affect_outcome, q2_5_deviations_balanced,
              q2_6_appropriate_analysis, q2_7_substantial_impact]
    inputs = [inp.upper() for inp in inputs]
    
    # Validate inputs
    valid_responses = ['Y', 'PY', 'PN', 'N', 'NI', 'NA']
    if not all(inp in valid_responses for inp in inputs):
        raise ValueError("Invalid response. Use: Y, PY, PN, N, NI, or NA")
    
    q2_1, q2_2, q2_3, q2_4, q2_5, q2_6, q2_7 = inputs
    
    # PART 1 ASSESSMENT (Questions 2.1 to 2.5)
    part1_risk, part1_reason = assess_part1_deviations(q2_1, q2_2, q2_3, q2_4, q2_5)
    
    # PART 2 ASSESSMENT (Questions 2.6 and 2.7)
    part2_risk, part2_reason = assess_part2_analysis(q2_6, q2_7)
    
    # COMBINE PARTS FOR OVERALL DOMAIN ASSESSMENT
    if part1_risk == 'Low' and part2_risk == 'Low':
        overall_risk = 'Low'
        reasoning = 'Low risk in both intervention fidelity and analysis components'
    elif part1_risk == 'High' or part2_risk == 'High':
        overall_risk = 'High'
        reasoning = f'High risk in {"Part 1 (intervention fidelity)" if part1_risk == "High" else "Part 2 (analysis)"}'
        if part1_risk == 'High' and part2_risk == 'High':
            reasoning = 'High risk in both intervention fidelity and analysis components'
    else:
        overall_risk = 'Some concerns'
        reasoning = 'Some concerns identified but not high risk in either component'
    
    return overall_risk, reasoning, {'part1': part1_risk, 'part2': part2_risk}


def assess_part1_deviations(q2_1, q2_2, q2_3, q2_4, q2_5):
    """Assess Part 1: Questions 2.1 to 2.5 (Intervention fidelity)"""
    # Check if both participants and personnel were unaware
    both_unaware = (q2_1 in ['N', 'PN'] and q2_2 in ['N', 'PN'])
    
    # Check if aware but no deviations occurred
    either_aware = (q2_1 in ['Y', 'PY', 'NI'] or q2_2 in ['Y', 'PY', 'NI'])
    no_deviations = (q2_3 in ['N', 'PN'])
    
    if both_unaware:
        return 'Low', 'Both participants and personnel unaware of intervention groups'
    elif either_aware and no_deviations:
        return 'Low', 'Awareness present but no deviations from intended intervention occurred'
    
    # HIGH RISK criteria
    if (either_aware and 
        q2_3 in ['Y', 'PY'] and 
        q2_4 in ['Y', 'PY', 'NI'] and 
        q2_5 in ['N', 'PN', 'NI']):
        return 'High', 'Awareness led to outcome-affecting deviations that were unbalanced between groups'
    
    # SOME CONCERNS - all other scenarios
    if q2_3 == 'NI':
        return 'Some concerns', 'No information available about whether deviations occurred'
    elif q2_3 in ['Y', 'PY']:
        if q2_4 in ['N', 'PN']:
            return 'Some concerns', 'Deviations occurred but were not likely to affect the outcome'
        elif q2_4 in ['Y', 'PY'] and q2_5 in ['Y', 'PY']:
            return 'Some concerns', 'Deviations occurred and may have affected outcome but were balanced between groups'
        else:
            return 'Some concerns', 'Deviations occurred with uncertain impact or balance'
    
    return 'Some concerns', 'Intermediate scenario not meeting low or high risk criteria'


def assess_part2_analysis(q2_6, q2_7):
    """Assess Part 2: Questions 2.6 and 2.7 (Analysis approach)"""
    # LOW RISK: An appropriate analysis was used to estimate the effect of assignment to intervention
    if q2_6 in ['Y', 'PY']:
        return 'Low', 'Appropriate analysis used to estimate effect of assignment to intervention'
    
    # HIGH RISK: An inappropriate analysis was used AND substantial impact on result
    if q2_6 in ['N', 'PN', 'NI'] and q2_7 in ['Y', 'PY', 'NI']:
        return 'High', 'Inappropriate analysis used with substantial impact on results'
    
    # SOME CONCERNS: Inappropriate analysis but no substantial impact
    if q2_6 in ['N', 'PN', 'NI'] and q2_7 in ['N', 'PN']:
        return 'Some concerns', 'Inappropriate analysis used but no substantial impact on results'
    
    return 'Some concerns', 'Uncertain analysis approach'


def assess_domain_3_missing_data(q3_1_complete_data, q3_2_evidence_no_bias, 
                                q3_3_could_depend_true_value, q3_4_likely_depend_true_value):
    """
    Domain 3: Risk of bias due to missing outcome data
    """
    # Normalize inputs
    inputs = [q3_1_complete_data, q3_2_evidence_no_bias, 
              q3_3_could_depend_true_value, q3_4_likely_depend_true_value]
    inputs = [inp.upper() for inp in inputs]
    
    # Validate inputs
    valid_responses = ['Y', 'PY', 'PN', 'N', 'NI', 'NA']
    if not all(inp in valid_responses for inp in inputs):
        raise ValueError("Invalid response. Use: Y, PY, PN, N, NI, or NA")
    
    q3_1, q3_2, q3_3, q3_4 = inputs
    
    # LOW RISK criteria (any one of these conditions)
    if q3_1 in ['Y', 'PY']:
        return ('Low', 'Outcome data available for all or nearly all randomized participants')
    
    if q3_2 in ['Y', 'PY']:
        return ('Low', 'Evidence provided that result was not biased by missing outcome data')
    
    if q3_3 in ['N', 'PN']:
        return ('Low', 'Missingness in the outcome could not depend on its true value')
    
    # HIGH RISK criteria
    if (q3_1 in ['N', 'PN', 'NI'] and 
        q3_2 in ['N', 'PN'] and 
        q3_3 in ['Y', 'PY', 'NI'] and 
        q3_4 in ['Y', 'PY', 'NI']):
        return ('High', 'Incomplete data with no evidence of no bias, and missingness likely depends on true value')
    
    # SOME CONCERNS criteria
    if (q3_1 in ['N', 'PN', 'NI'] and 
        q3_2 in ['N', 'PN'] and 
        q3_3 in ['Y', 'PY', 'NI'] and 
        q3_4 in ['N', 'PN']):
        return ('Some concerns', 'Incomplete data with potential for bias, but missingness unlikely to depend on true value')
    
    # Handle edge cases
    if q3_2 == 'NI':
        if q3_3 in ['N', 'PN']:
            return ('Low', 'No information about bias evidence, but missingness could not depend on true value')
        else:
            return ('Some concerns', 'No information about bias evidence and uncertain relationship between missingness and true value')
    
    return ('Some concerns', 'Intermediate scenario with some missing data and uncertain bias potential')


def assess_domain_4_outcome_measurement(q4_1_method_inappropriate, q4_2_differ_between_groups,
                                       q4_3_assessors_aware, q4_4_could_be_influenced, 
                                       q4_5_likely_influenced):
    """
    Domain 4: Risk of bias in measurement of the outcome
    """
    # Normalize inputs
    inputs = [q4_1_method_inappropriate, q4_2_differ_between_groups,
              q4_3_assessors_aware, q4_4_could_be_influenced, q4_5_likely_influenced]
    inputs = [inp.upper() for inp in inputs]
    
    # Validate inputs
    valid_responses = ['Y', 'PY', 'PN', 'N', 'NI', 'NA']
    if not all(inp in valid_responses for inp in inputs):
        raise ValueError("Invalid response. Use: Y, PY, PN, N, NI, or NA")
    
    q4_1, q4_2, q4_3, q4_4, q4_5 = inputs
    
    # HIGH RISK criteria (any one of these conditions)
    if q4_1 in ['Y', 'PY']:
        return ('High', 'Inappropriate method of measuring the outcome')
    
    if q4_2 in ['Y', 'PY']:
        return ('High', 'Measurement or ascertainment of outcome differed between intervention groups')
    
    if (q4_3 in ['Y', 'PY', 'NI'] and 
        q4_4 in ['Y', 'PY', 'NI'] and 
        q4_5 in ['Y', 'PY', 'NI']):
        return ('High', 'Assessment likely influenced by knowledge of intervention assignment')
    
    # LOW RISK criteria
    method_appropriate = q4_1 in ['N', 'PN', 'NI']
    measurement_consistent = q4_2 in ['N', 'PN']
    assessors_blinded = q4_3 in ['N', 'PN']
    cannot_be_influenced = (q4_3 in ['Y', 'PY', 'NI'] and q4_4 in ['N', 'PN'])
    
    if method_appropriate and measurement_consistent and (assessors_blinded or cannot_be_influenced):
        if assessors_blinded:
            return ('Low', 'Appropriate measurement method, consistent between groups, and assessors blinded')
        else:
            return ('Low', 'Appropriate measurement method, consistent between groups, and assessment cannot be influenced by knowledge')
    
    # SOME CONCERNS criteria
    if (method_appropriate and measurement_consistent and 
        q4_3 in ['Y', 'PY', 'NI'] and q4_4 in ['Y', 'PY', 'NI'] and q4_5 in ['N', 'PN']):
        return ('Some concerns', 'Potential for assessment bias exists but unlikely to have influenced results')
    
    if (method_appropriate and q4_2 == 'NI' and (assessors_blinded or cannot_be_influenced)):
        if assessors_blinded:
            return ('Some concerns', 'No information about differential measurement, but assessors were blinded')
        else:
            return ('Some concerns', 'No information about differential measurement, but assessment cannot be influenced')
    
    if method_appropriate and q4_2 == 'NI':
        return ('Some concerns', 'No information about whether measurement differed between groups')
    
    return ('Some concerns', 'Intermediate scenario with some potential for measurement bias')


def assess_domain_5_selective_reporting(q5_1_accordance_with_plan, q5_2_selected_from_multiple_outcomes,
                                       q5_3_selected_from_multiple_analyses):
    """
    Domain 5: Risk of bias in selection of the reported result
    """
    # Normalize inputs
    inputs = [q5_1_accordance_with_plan, q5_2_selected_from_multiple_outcomes,
              q5_3_selected_from_multiple_analyses]
    inputs = [inp.upper() for inp in inputs]
    
    # Validate inputs
    valid_responses = ['Y', 'PY', 'PN', 'N', 'NI']
    if not all(inp in valid_responses for inp in inputs):
        raise ValueError("Invalid response. Use: Y, PY, PN, N, or NI")
    
    q5_1, q5_2, q5_3 = inputs
    
    # HIGH RISK criteria
    if q5_2 in ['Y', 'PY']:
        return ('High', 'Result likely selected from multiple eligible outcome measurements based on results')
    
    if q5_3 in ['Y', 'PY']:
        return ('High', 'Result likely selected from multiple eligible analyses based on results')
    
    # LOW RISK criteria
    if (q5_1 in ['Y', 'PY'] and 
        q5_2 in ['N', 'PN'] and 
        q5_3 in ['N', 'PN']):
        return ('Low', 'Analysis according to pre-specified plan with no evidence of selective reporting')
    
    # SOME CONCERNS criteria
    if (q5_1 in ['N', 'PN', 'NI'] and 
        q5_2 in ['N', 'PN'] and 
        q5_3 in ['N', 'PN']):
        return ('Some concerns', 'No pre-specified analysis plan, but no evidence of selective reporting')
    
    if ((q5_2 == 'NI' and q5_3 in ['N', 'PN']) or 
        (q5_2 in ['N', 'PN'] and q5_3 == 'NI') or 
        (q5_2 == 'NI' and q5_3 == 'NI')):
        return ('Some concerns', 'Insufficient information about potential selective reporting')
    
    return ('Some concerns', 'Unclear evidence regarding selective reporting practices')


def assess_overall_rob2(domain1_risk, domain2_risk, domain3_risk, domain4_risk, domain5_risk):
    """
    Overall Risk of Bias Assessment combining all five domains
    """
    # Normalize inputs
    risks = [domain1_risk.strip(), domain2_risk.strip(), domain3_risk.strip(), 
             domain4_risk.strip(), domain5_risk.strip()]
    
    # Validate inputs
    valid_risks = ['Low', 'Some concerns', 'High']
    if not all(risk in valid_risks for risk in risks):
        raise ValueError("All domain risks must be: 'Low', 'Some concerns', or 'High'")
    
    domain_names = [
        "Domain 1 (Randomization)",
        "Domain 2 (Deviations)", 
        "Domain 3 (Missing data)",
        "Domain 4 (Outcome measurement)",
        "Domain 5 (Selective reporting)"
    ]
    
    # Count risk levels
    high_count = risks.count('High')
    some_concerns_count = risks.count('Some concerns')
    low_count = risks.count('Low')
    
    # Apply RoB 2 overall criteria
    if high_count >= 1:
        # HIGH RISK: At least one domain at high risk
        overall_risk = 'High'
        high_domains = [domain_names[i] for i, risk in enumerate(risks) if risk == 'High']
        reasoning = f"High risk of bias in: {', '.join(high_domains)}"
        
    elif some_concerns_count == 0:
        # LOW RISK: All domains at low risk
        overall_risk = 'Low'
        reasoning = "Low risk of bias across all domains"
        
    elif some_concerns_count >= 3:
        # HIGH RISK: Multiple domains with some concerns substantially lower confidence
        overall_risk = 'High'
        concerns_domains = [domain_names[i] for i, risk in enumerate(risks) if risk == 'Some concerns']
        reasoning = f"Some concerns in multiple domains substantially lower confidence: {', '.join(concerns_domains)}"
        
    else:
        # SOME CONCERNS: Some concerns in 1-2 domains, no high risk
        overall_risk = 'Some concerns'
        concerns_domains = [domain_names[i] for i, risk in enumerate(risks) if risk == 'Some concerns']
        reasoning = f"Some concerns identified in: {', '.join(concerns_domains)}"
    
    return overall_risk, reasoning


def calculate_rob2_assessment(assessment_responses):
    """
    Calculate complete RoB 2.0 assessment from user responses
    
    Args:
        assessment_responses (dict): Dictionary containing responses to all RoB 2.0 questions
        
    Returns:
        dict: Complete assessment results including domain-specific and overall assessments
    """
    results = {}
    
    # Domain 1: Randomization
    if all(key in assessment_responses for key in ['1.1', '1.2', '1.3']):
        d1_risk, d1_reason = assess_domain_1_randomization(
            assessment_responses['1.1'],
            assessment_responses['1.2'], 
            assessment_responses['1.3']
        )
        results['domain_1'] = {
            'risk': d1_risk,
            'reasoning': d1_reason
        }
    
    # Domain 2: Deviations 
    if all(key in assessment_responses for key in ['2.1', '2.2', '2.3', '2.4', '2.5', '2.6', '2.7']):
        d2_risk, d2_reason, d2_details = assess_domain_2_deviations(
            assessment_responses['2.1'],
            assessment_responses['2.2'],
            assessment_responses['2.3'],
            assessment_responses['2.4'],
            assessment_responses['2.5'],
            assessment_responses['2.6'],
            assessment_responses['2.7']
        )
        results['domain_2'] = {
            'risk': d2_risk,
            'reasoning': d2_reason,
            'details': d2_details
        }
    
    # Domain 3: Missing data
    if all(key in assessment_responses for key in ['3.1', '3.2', '3.3', '3.4']):
        d3_risk, d3_reason = assess_domain_3_missing_data(
            assessment_responses['3.1'],
            assessment_responses['3.2'],
            assessment_responses['3.3'],
            assessment_responses['3.4']
        )
        results['domain_3'] = {
            'risk': d3_risk,
            'reasoning': d3_reason
        }
    
    # Domain 4: Outcome measurement
    if all(key in assessment_responses for key in ['4.1', '4.2', '4.3', '4.4', '4.5']):
        d4_risk, d4_reason = assess_domain_4_outcome_measurement(
            assessment_responses['4.1'],
            assessment_responses['4.2'],
            assessment_responses['4.3'],
            assessment_responses['4.4'],
            assessment_responses['4.5']
        )
        results['domain_4'] = {
            'risk': d4_risk,
            'reasoning': d4_reason
        }
    
    # Domain 5: Selective reporting
    if all(key in assessment_responses for key in ['5.1', '5.2', '5.3']):
        d5_risk, d5_reason = assess_domain_5_selective_reporting(
            assessment_responses['5.1'],
            assessment_responses['5.2'],
            assessment_responses['5.3']
        )
        results['domain_5'] = {
            'risk': d5_risk,
            'reasoning': d5_reason
        }
    
    # Overall assessment
    if all(f'domain_{i}' in results for i in range(1, 6)):
        overall_risk, overall_reason = assess_overall_rob2(
            results['domain_1']['risk'],
            results['domain_2']['risk'],
            results['domain_3']['risk'],
            results['domain_4']['risk'],
            results['domain_5']['risk']
        )
        results['overall'] = {
            'risk': overall_risk,
            'reasoning': overall_reason
        }
    
    return results
