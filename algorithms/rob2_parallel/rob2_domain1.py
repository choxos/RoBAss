def assess_randomization_bias(q1_sequence_random, q2_allocation_concealed, q3_baseline_imbalance):
    """
    RoB 2 Domain 1: Risk of bias arising from the randomization process
    
    Parameters:
    q1_sequence_random (str): Was the allocation sequence random?
        - 'Y': Yes
        - 'PY': Probably yes  
        - 'PN': Probably no
        - 'N': No
        - 'NI': No information
        
    q2_allocation_concealed (str): Was the allocation sequence concealed?
        - 'Y': Yes
        - 'PY': Probably yes
        - 'PN': Probably no  
        - 'N': No
        - 'NI': No information
        
    q3_baseline_imbalance (str): Did baseline differences suggest a problem with randomization?
        - 'Y': Yes
        - 'PY': Probably yes
        - 'PN': Probably no
        - 'N': No
        - 'NI': No information
        
    Returns:
    tuple: (risk_level, reasoning)
        risk_level: 'Low', 'Some concerns', or 'High'
        reasoning: explanation of the assessment
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
    # (i) The allocation sequence was adequately concealed AND
    # (ii.1) Any baseline differences observed between intervention groups appear to be compatible with chance
    # OR (ii.2) There is no information about baseline imbalances
    # AND
    # (iii.1) The allocation sequence was random OR (iii.2) There is no information about whether the allocation sequence was random
    
    if (q2 in ['Y', 'PY'] and  # Allocation sequence adequately concealed
        q3 in ['N', 'PN', 'NI'] and  # No concerning baseline imbalances
        q1 in ['Y', 'PY', 'NI']):  # Sequence was random or no info
        return ('Low', 'Allocation sequence adequately concealed, no concerning baseline imbalances, and randomization appropriate')
    
    # HIGH RISK criteria  
    # (i) The allocation sequence was not adequately concealed OR
    # (ii.1) There is no information about concealment of the allocation sequence AND
    # (ii.2) Baseline differences between intervention groups suggest a problem with the randomization process
    
    if (q2 in ['N', 'PN'] or  # Allocation sequence not adequately concealed
        (q2 == 'NI' and q3 in ['Y', 'PY'])):  # No info on concealment AND baseline imbalances suggest problem
        return ('High', 'Allocation sequence not adequately concealed or baseline imbalances suggest randomization problems')
    
    # Additional HIGH RISK: Any response to sequence generation that is N/PN with baseline imbalances
    if q1 in ['N', 'PN'] and q3 in ['Y', 'PY']:
        return ('High', 'Non-random sequence generation with baseline imbalances suggesting problems')
    
    # SOME CONCERNS - all other combinations
    # This includes scenarios like:
    # - Adequate concealment but concerning baseline imbalances
    # - No information about concealment but no baseline imbalances  
    # - Various other intermediate scenarios
    
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


def detailed_assessment(q1, q2, q3, study_info=""):
    """
    Provides a detailed assessment with all signaling questions and recommendations
    """
    risk, reasoning = assess_randomization_bias(q1, q2, q3)
    
    print("=== RoB 2 Domain 1: Bias arising from the randomization process ===")
    if study_info:
        print(f"Study: {study_info}")
    print()
    
    print("Signaling Questions:")
    print(f"1.1 Was the allocation sequence random? {q1}")
    print(f"1.2 Was the allocation sequence concealed? {q2}")  
    print(f"1.3 Did baseline differences suggest a problem with randomization? {q3}")
    print()
    
    print(f"Risk Assessment: {risk}")
    print(f"Reasoning: {reasoning}")
    print()
    
    # Additional guidance based on risk level
    if risk == "Low":
        print("✓ This domain poses low risk of bias to study results")
    elif risk == "Some concerns":
        print("⚠ This domain raises some concerns about potential bias")
        print("Consider: Additional investigation of randomization methods may be warranted")
    else:  # High risk
        print("⚠ This domain poses high risk of bias")
        print("Consider: Results should be interpreted with significant caution due to randomization concerns")
    
    return risk, reasoning


# Example usage and test cases
if __name__ == "__main__":
    print("Testing RoB 2 Domain 1 Assessment Algorithm\n")
    
    # Test case 1: Low risk scenario
    print("Test 1 - Low Risk Scenario:")
    detailed_assessment('Y', 'Y', 'N', "Example RCT with proper randomization")
    print("-" * 60)
    
    # Test case 2: Some concerns scenario  
    print("Test 2 - Some Concerns Scenario:")
    detailed_assessment('Y', 'Y', 'PY', "RCT with baseline imbalances")
    print("-" * 60)
    
    # Test case 3: High risk scenario
    print("Test 3 - High Risk Scenario:")
    detailed_assessment('N', 'N', 'Y', "RCT with poor randomization")
    print("-" * 60)
    
    # Test case 4: Edge case - no information
    print("Test 4 - Limited Information Scenario:")
    detailed_assessment('NI', 'NI', 'NI', "RCT with limited reporting")
