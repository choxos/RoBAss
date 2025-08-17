def assess_missing_outcome_bias(q3_1_complete_data, q3_2_evidence_no_bias, 
                               q3_3_could_depend_true_value, q3_4_likely_depend_true_value):
    """
    RoB 2 Domain 3: Risk of bias due to missing outcome data
    
    Parameters:
    q3_1_complete_data (str): Were outcome data available for all, or nearly all, randomized participants?
    q3_2_evidence_no_bias (str): Is there evidence that the result was not biased by missing outcome data?
    q3_3_could_depend_true_value (str): Could missingness in the outcome depend on its true value?
    q3_4_likely_depend_true_value (str): Is it likely that missingness in the outcome depended on its true value?
    
    Response options: 'Y', 'PY', 'PN', 'N', 'NI', 'NA'
    
    Returns:
    tuple: (risk_level, reasoning)
    """
    
    # Normalize inputs
    q3_1 = q3_1_complete_data.upper()
    q3_2 = q3_2_evidence_no_bias.upper()
    q3_3 = q3_3_could_depend_true_value.upper()
    q3_4 = q3_4_likely_depend_true_value.upper()
    
    # Validate inputs
    valid_responses = ['Y', 'PY', 'PN', 'N', 'NI', 'NA']
    if not all(inp in valid_responses for inp in [q3_1, q3_2, q3_3, q3_4]):
        raise ValueError("Invalid response. Use: Y, PY, PN, N, NI, or NA")
    
    # LOW RISK criteria (any one of these conditions):
    # (i) Outcome data were available for all, or nearly all, randomized participants
    if q3_1 in ['Y', 'PY']:
        return ('Low', 'Outcome data available for all or nearly all randomized participants')
    
    # (ii) There is evidence that the result was not biased by missing outcome data
    if q3_2 in ['Y', 'PY']:
        return ('Low', 'Evidence provided that result was not biased by missing outcome data')
    
    # (iii) Missingness in the outcome could not depend on its true value
    if q3_3 in ['N', 'PN']:
        return ('Low', 'Missingness in the outcome could not depend on its true value')
    
    # HIGH RISK criteria (all conditions must be met):
    # (i) Outcome data were NOT available for all, or nearly all, randomized participants
    # AND (ii) There is NOT evidence that the result was not biased by missing outcome data
    # AND (iii) Missingness in the outcome could depend on its true value
    # AND (iv) It is likely that missingness in the outcome depended on its true value
    
    if (q3_1 in ['N', 'PN', 'NI'] and 
        q3_2 in ['N', 'PN'] and 
        q3_3 in ['Y', 'PY', 'NI'] and 
        q3_4 in ['Y', 'PY', 'NI']):
        return ('High', 'Incomplete data with no evidence of no bias, and missingness likely depends on true value')
    
    # SOME CONCERNS criteria (all conditions must be met):
    # (i) Outcome data were NOT available for all, or nearly all, randomized participants
    # AND (ii) There is NOT evidence that the result was not biased by missing outcome data
    # AND (iii) Missingness in the outcome could depend on its true value
    # AND (iv) It is NOT likely that missingness in the outcome depended on its true value
    
    if (q3_1 in ['N', 'PN', 'NI'] and 
        q3_2 in ['N', 'PN'] and 
        q3_3 in ['Y', 'PY', 'NI'] and 
        q3_4 in ['N', 'PN']):
        return ('Some concerns', 'Incomplete data with potential for bias, but missingness unlikely to depend on true value')
    
    # Handle edge cases and No Information scenarios
    if q3_2 == 'NI':
        if q3_3 in ['N', 'PN']:
            return ('Low', 'No information about bias evidence, but missingness could not depend on true value')
        else:
            return ('Some concerns', 'No information about bias evidence and uncertain relationship between missingness and true value')
    
    # Default fallback for any remaining scenarios
    return ('Some concerns', 'Intermediate scenario with some missing data and uncertain bias potential')


def detailed_assessment_domain3(q3_1, q3_2, q3_3, q3_4, study_info="", 
                               missing_percentage=None, reasons_for_missing=None):
    """
    Provides detailed assessment with contextual information
    
    Additional parameters:
    missing_percentage (float): Percentage of participants with missing outcome data
    reasons_for_missing (str): Description of reasons for missing data
    """
    risk, reasoning = assess_missing_outcome_bias(q3_1, q3_2, q3_3, q3_4)
    
    print("=== RoB 2 Domain 3: Bias due to missing outcome data ===")
    if study_info:
        print(f"Study: {study_info}")
    if missing_percentage is not None:
        print(f"Missing data: {missing_percentage:.1f}% of participants")
    if reasons_for_missing:
        print(f"Reasons for missingness: {reasons_for_missing}")
    print()
    
    print("Signaling Questions:")
    print(f"3.1 Were outcome data available for all, or nearly all, participants? {q3_1}")
    
    # Conditional questions based on flowchart logic
    if q3_1 in ['N', 'PN', 'NI']:
        print(f"3.2 Is there evidence that result was not biased by missing data? {q3_2}")
        
        if q3_2 in ['N', 'PN']:
            print(f"3.3 Could missingness in outcome depend on its true value? {q3_3}")
            
            if q3_3 in ['Y', 'PY', 'NI']:
                print(f"3.4 Is it likely that missingness depended on its true value? {q3_4}")
    
    print()
    print(f"Risk Assessment: {risk}")
    print(f"Reasoning: {reasoning}")
    print()
    
    # Additional guidance based on risk level and context
    if risk == "Low":
        print("✓ This domain poses low risk of bias")
        if q3_1 in ['Y', 'PY']:
            print("Complete or nearly complete outcome data available")
        elif q3_2 in ['Y', 'PY']:
            print("Evidence provided that missing data did not bias results")
        else:
            print("Missing data pattern unlikely to introduce bias")
    
    elif risk == "Some concerns":
        print("⚠ This domain raises some concerns about potential bias")
        print("Recommendations:")
        print("- Consider sensitivity analyses to assess impact of missing data")
        print("- Examine patterns of missingness across treatment groups")
        print("- Assess plausibility of missing data assumptions")
        
        if missing_percentage and missing_percentage > 20:
            print(f"- High level of missing data ({missing_percentage:.1f}%) increases concern")
    
    else:  # High risk
        print("⚠ This domain poses high risk of bias")
        print("Critical issues:")
        print("- Substantial missing outcome data")
        print("- No evidence that results are unbiased")
        print("- Missing data likely related to true outcome values")
        print("- Results should be interpreted with significant caution")
        print("- Multiple sensitivity analyses strongly recommended")
    
    return risk, reasoning


def calculate_missing_data_percentage(total_randomized, total_analyzed):
    """
    Helper function to calculate percentage of missing outcome data
    """
    if total_randomized <= 0:
        raise ValueError("Total randomized must be positive")
    
    missing = total_randomized - total_analyzed
    percentage = (missing / total_randomized) * 100
    
    return percentage


def assess_missing_data_pattern(missing_intervention, total_intervention, 
                              missing_control, total_control):
    """
    Helper function to assess differential missing data patterns between groups
    """
    pct_missing_intervention = (missing_intervention / total_intervention) * 100
    pct_missing_control = (missing_control / total_control) * 100
    
    difference = abs(pct_missing_intervention - pct_missing_control)
    
    pattern_info = {
        'intervention_missing_pct': pct_missing_intervention,
        'control_missing_pct': pct_missing_control,
        'difference': difference,
        'balanced': difference < 5.0  # Arbitrary threshold for "balanced"
    }
    
    return pattern_info


# Example usage and test cases
if __name__ == "__main__":
    print("Testing RoB 2 Domain 3 Assessment Algorithm\n")
    
    # Test case 1: Low risk - complete data
    print("Test 1 - Low Risk (Complete data):")
    detailed_assessment_domain3('Y', 'NA', 'NA', 'NA', 
                              "RCT with complete follow-up", 
                              missing_percentage=2.0)
    print("-" * 80)
    
    # Test case 2: Low risk - evidence of no bias
    print("Test 2 - Low Risk (Evidence of no bias):")
    detailed_assessment_domain3('N', 'Y', 'NA', 'NA',
                              "RCT with sensitivity analysis showing no impact",
                              missing_percentage=15.0,
                              reasons_for_missing="Administrative censoring at study end")
    print("-" * 80)
    
    # Test case 3: Some concerns
    print("Test 3 - Some Concerns (Missing data, unlikely to depend on outcome):")
    detailed_assessment_domain3('N', 'N', 'Y', 'N',
                              "RCT with some missing data",
                              missing_percentage=12.0,
                              reasons_for_missing="Lost to follow-up, moving, administrative")
    print("-" * 80)
    
    # Test case 4: High risk
    print("Test 4 - High Risk (Missing data likely depends on outcome):")
    detailed_assessment_domain3('N', 'N', 'Y', 'Y',
                              "RCT with outcome-related dropout",
                              missing_percentage=25.0,
                              reasons_for_missing="Withdrawal due to side effects and lack of efficacy")
    print("-" * 80)
    
    # Test case 5: Missing data pattern analysis
    print("Test 5 - Missing Data Pattern Analysis:")
    pattern = assess_missing_data_pattern(25, 100, 15, 100)  # 25% vs 15% missing
    print("Missing data pattern:")
    print(f"Intervention group: {pattern['intervention_missing_pct']:.1f}% missing")
    print(f"Control group: {pattern['control_missing_pct']:.1f}% missing")
    print(f"Difference: {pattern['difference']:.1f} percentage points")
    print(f"Balanced pattern: {'Yes' if pattern['balanced'] else 'No'}")
    print()
    
    detailed_assessment_domain3('N', 'N', 'Y', 'PY',
                              "RCT with differential missing data",
                              missing_percentage=20.0,
                              reasons_for_missing="Higher dropout in intervention group")
