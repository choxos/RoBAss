def assess_selection_bias(q5_1_accordance_with_plan, q5_2_selected_from_multiple_outcomes,
                         q5_3_selected_from_multiple_analyses):
    """
    RoB 2 Domain 5: Risk of bias in selection of the reported result
    
    Parameters:
    q5_1_accordance_with_plan (str): Were the data that produced this result analysed in accordance with a pre-specified plan that was finalized before unblinded outcome data were available for analysis?
    q5_2_selected_from_multiple_outcomes (str): Is the numerical result being assessed likely to have been selected, on the basis of the results, from multiple eligible outcome measurements (e.g. scales, definitions, time points) within the outcome domain?
    q5_3_selected_from_multiple_analyses (str): Is the numerical result being assessed likely to have been selected, on the basis of the results, from multiple eligible analyses of the data?
    
    Response options: 'Y', 'PY', 'PN', 'N', 'NI'
    
    Returns:
    tuple: (risk_level, reasoning)
    """
    
    # Normalize inputs
    q5_1 = q5_1_accordance_with_plan.upper()
    q5_2 = q5_2_selected_from_multiple_outcomes.upper()
    q5_3 = q5_3_selected_from_multiple_analyses.upper()
    
    # Validate inputs
    valid_responses = ['Y', 'PY', 'PN', 'N', 'NI']
    if not all(inp in valid_responses for inp in [q5_1, q5_2, q5_3]):
        raise ValueError("Invalid response. Use: Y, PY, PN, N, or NI")
    
    # HIGH RISK criteria (any one of these conditions):
    # (i) The result being assessed is likely to have been selected, on the basis of the results, 
    #     from multiple eligible outcome measurements within the outcome domain
    # OR
    # (ii) The result being assessed is likely to have been selected, on the basis of the results, 
    #      from multiple eligible analyses of the data
    
    if q5_2 in ['Y', 'PY']:
        return ('High', 'Result likely selected from multiple eligible outcome measurements based on results')
    
    if q5_3 in ['Y', 'PY']:
        return ('High', 'Result likely selected from multiple eligible analyses based on results')
    
    # LOW RISK criteria (all conditions must be met):
    # (i) The data were analysed in accordance with a pre-specified plan that was finalised 
    #     before unblinded outcome data were available for analysis
    # AND
    # (ii) The result being assessed is unlikely to have been selected, on the basis of the results, 
    #      from multiple eligible outcome measurements within the outcome domain
    # AND  
    # (iii) Reported outcome data are unlikely to have been selected, on the basis of the results, 
    #       from multiple eligible analyses of the data
    
    if (q5_1 in ['Y', 'PY'] and 
        q5_2 in ['N', 'PN'] and 
        q5_3 in ['N', 'PN']):
        return ('Low', 'Analysis according to pre-specified plan with no evidence of selective reporting')
    
    # SOME CONCERNS criteria:
    # (i.1) The data were NOT analysed in accordance with a pre-specified plan that was finalised 
    #       before unblinded outcome data were available for analysis
    # AND
    # (i.2) The result being assessed is unlikely to have been selected from multiple eligible outcome measurements
    # AND
    # (i.3) The result being assessed is unlikely to have been selected from multiple eligible analyses
    # OR
    # (ii) There is no information on whether the result being assessed is likely to have been selected 
    #      from multiple eligible outcome measurements AND from multiple eligible analyses
    
    # Scenario 1: No pre-specified plan but no evidence of selective reporting
    if (q5_1 in ['N', 'PN', 'NI'] and 
        q5_2 in ['N', 'PN'] and 
        q5_3 in ['N', 'PN']):
        return ('Some concerns', 'No pre-specified analysis plan, but no evidence of selective reporting')
    
    # Scenario 2: No information about selective reporting
    if ((q5_2 == 'NI' and q5_3 in ['N', 'PN']) or 
        (q5_2 in ['N', 'PN'] and q5_3 == 'NI') or 
        (q5_2 == 'NI' and q5_3 == 'NI')):
        return ('Some concerns', 'Insufficient information about potential selective reporting')
    
    # Default fallback for any remaining edge cases
    return ('Some concerns', 'Unclear evidence regarding selective reporting practices')


def detailed_assessment_domain5(q5_1, q5_2, q5_3, study_info="",
                               protocol_details=None, analysis_plan_timing=None,
                               multiple_outcomes_details=None, multiple_analyses_details=None):
    """
    Provides detailed assessment with contextual information
    
    Additional parameters:
    protocol_details (str): Information about study protocol and pre-specification
    analysis_plan_timing (str): When analysis plan was finalized
    multiple_outcomes_details (str): Details about multiple outcome measurements available
    multiple_analyses_details (str): Details about multiple analyses performed
    """
    risk, reasoning = assess_selection_bias(q5_1, q5_2, q5_3)
    
    print("=== RoB 2 Domain 5: Bias in selection of the reported result ===")
    if study_info:
        print(f"Study: {study_info}")
    if protocol_details:
        print(f"Protocol: {protocol_details}")
    if analysis_plan_timing:
        print(f"Analysis plan timing: {analysis_plan_timing}")
    print()
    
    print("Signaling Questions:")
    print(f"5.1 Were data analysed according to pre-specified plan finalized before unblinding? {q5_1}")
    print(f"5.2 Is result likely selected from multiple eligible outcome measurements? {q5_2}")
    print(f"5.3 Is result likely selected from multiple eligible analyses? {q5_3}")
    
    if multiple_outcomes_details:
        print(f"    Multiple outcomes context: {multiple_outcomes_details}")
    if multiple_analyses_details:
        print(f"    Multiple analyses context: {multiple_analyses_details}")
    
    print()
    print(f"Risk Assessment: {risk}")
    print(f"Reasoning: {reasoning}")
    print()
    
    # Additional guidance based on risk level and context
    if risk == "Low":
        print("✓ This domain poses low risk of bias")
        print("Analysis appears to follow pre-specified plan without selective reporting")
        print("Key strengths:")
        print("- Pre-specified analysis plan finalized before unblinding")
        print("- No evidence of outcome selection based on results")
        print("- No evidence of analysis selection based on results")
        
    elif risk == "Some concerns":
        print("⚠ This domain raises some concerns about potential selective reporting")
        
        if q5_1 in ['N', 'PN', 'NI']:
            print("Issues identified:")
            print("- No evidence of pre-specified analysis plan or plan not finalized before unblinding")
            
        if 'NI' in [q5_2, q5_3]:
            print("- Insufficient information about selective reporting practices")
            
        print("Recommendations:")
        print("- Check for study protocol or statistical analysis plan")
        print("- Look for evidence of trial registration with pre-specified outcomes")
        print("- Consider whether reported results align with study objectives")
        
    else:  # High risk
        print("⚠ This domain poses high risk of bias")
        print("Evidence of selective reporting identified:")
        
        if q5_2 in ['Y', 'PY']:
            print("- Result likely selected from multiple outcome measurements based on findings")
            print("  (e.g., choosing favorable scale, time point, or outcome definition)")
            
        if q5_3 in ['Y', 'PY']:
            print("- Result likely selected from multiple analyses based on findings")
            print("  (e.g., choosing favorable statistical method, subgroup, or adjustment)")
            
        print("Critical considerations:")
        print("- Results should be interpreted with significant caution")
        print("- Effect estimates may be inflated due to selective reporting")
        print("- Consider impact on meta-analysis and evidence synthesis")
    
    return risk, reasoning


def assess_protocol_availability(protocol_registered, protocol_date, study_start_date, 
                               outcomes_match_protocol, analyses_match_protocol):
    """
    Helper function to assess quality of pre-specification based on protocol information
    
    Parameters:
    protocol_registered (bool): Was study protocol registered?
    protocol_date (str): Date protocol was registered/finalized  
    study_start_date (str): Date study started recruitment
    outcomes_match_protocol (bool): Do reported outcomes match protocol?
    analyses_match_protocol (bool): Do reported analyses match protocol?
    
    Returns:
    dict: Assessment of pre-specification quality
    """
    assessment = {
        'pre_specification_quality': 'Unknown',
        'concerns': [],
        'strengths': []
    }
    
    if not protocol_registered:
        assessment['pre_specification_quality'] = 'Poor'
        assessment['concerns'].append('No registered protocol available')
        return assessment
    
    # Check timing of protocol registration
    if protocol_date and study_start_date:
        if protocol_date <= study_start_date:
            assessment['strengths'].append('Protocol registered before study start')
        else:
            assessment['concerns'].append('Protocol registered after study start (retrospective registration)')
    
    # Check consistency with protocol
    if outcomes_match_protocol:
        assessment['strengths'].append('Reported outcomes match protocol')
    else:
        assessment['concerns'].append('Reported outcomes differ from protocol')
    
    if analyses_match_protocol:
        assessment['strengths'].append('Reported analyses match protocol')
    else:
        assessment['concerns'].append('Reported analyses differ from protocol')
    
    # Overall quality assessment
    if len(assessment['concerns']) == 0:
        assessment['pre_specification_quality'] = 'High'
    elif len(assessment['concerns']) <= 1:
        assessment['pre_specification_quality'] = 'Moderate'
    else:
        assessment['pre_specification_quality'] = 'Poor'
    
    return assessment


# Example usage and test cases
if __name__ == "__main__":
    print("Testing RoB 2 Domain 5 Assessment Algorithm\n")
    
    # Test case 1: Low risk - pre-specified plan, no selection
    print("Test 1 - Low Risk (Pre-specified plan, no selective reporting):")
    detailed_assessment_domain5('Y', 'N', 'N',
                               "RCT with registered protocol",
                               protocol_details="Registered on ClinicalTrials.gov before recruitment",
                               analysis_plan_timing="Statistical analysis plan finalized before database lock")
    print("-" * 80)
    
    # Test case 2: Some concerns - no pre-specified plan but no selection
    print("Test 2 - Some Concerns (No pre-specified plan):")
    detailed_assessment_domain5('N', 'N', 'N',
                               "RCT without detailed analysis plan",
                               protocol_details="Basic protocol available but limited analysis details")
    print("-" * 80)
    
    # Test case 3: Some concerns - no information about selection
    print("Test 3 - Some Concerns (No information about selective reporting):")
    detailed_assessment_domain5('Y', 'NI', 'NI',
                               "RCT with limited reporting details",
                               analysis_plan_timing="Analysis plan available",
                               multiple_outcomes_details="Multiple scales mentioned but unclear which was primary")
    print("-" * 80)
    
    # Test case 4: High risk - outcome selection
    print("Test 4 - High Risk (Outcome selection based on results):")
    detailed_assessment_domain5('N', 'Y', 'N',
                               "Study with evidence of outcome switching",
                               multiple_outcomes_details="Primary outcome changed from protocol; favorable secondary outcome reported as primary")
    print("-" * 80)
    
    # Test case 5: High risk - analysis selection
    print("Test 5 - High Risk (Analysis selection based on results):")
    detailed_assessment_domain5('Y', 'N', 'Y',
                               "Study with multiple analysis approaches",
                               multiple_analyses_details="Per-protocol analysis reported after ITT analysis showed non-significant results")
    print("-" * 80)
    
    # Test case 6: Protocol assessment
    print("Test 6 - Protocol Quality Assessment:")
    protocol_assessment = assess_protocol_availability(
        protocol_registered=True,
        protocol_date="2020-01-15",
        study_start_date="2020-02-01", 
        outcomes_match_protocol=True,
        analyses_match_protocol=False
    )
    
    print("Protocol Assessment:")
    print(f"Pre-specification quality: {protocol_assessment['pre_specification_quality']}")
    if protocol_assessment['strengths']:
        print("Strengths:", "; ".join(protocol_assessment['strengths']))
    if protocol_assessment['concerns']:
        print("Concerns:", "; ".join(protocol_assessment['concerns']))
    print()
    
    # Corresponding Domain 5 assessment
    detailed_assessment_domain5('PY', 'N', 'PY',
                               "RCT with mixed protocol adherence",
                               protocol_details="Protocol registered before study start",
                               multiple_analyses_details="Unplanned subgroup analysis reported")
