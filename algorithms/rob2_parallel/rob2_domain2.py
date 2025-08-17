def assess_deviations_bias(q2_1_participants_aware, q2_2_personnel_aware, q2_3_deviations_occurred,
                          q2_4_deviations_affect_outcome, q2_5_deviations_balanced,
                          q2_6_appropriate_analysis, q2_7_substantial_impact):
    """
    RoB 2 Domain 2: Risk of bias due to deviations from intended interventions 
    (effect of assignment to intervention)
    
    This domain is assessed in two parts and then combined.
    
    Parameters:
    q2_1_participants_aware (str): Were participants aware of their assigned intervention?
    q2_2_personnel_aware (str): Were carers and people delivering the interventions aware of assigned interventions?
    q2_3_deviations_occurred (str): If Y/PY to 2.1 or 2.2: Were there deviations from intended intervention that arose because of the trial context?
    q2_4_deviations_affect_outcome (str): If Y/PY to 2.3: Were these deviations likely to have affected the outcome?
    q2_5_deviations_balanced (str): If Y/PY to 2.4: Were these deviations balanced between groups?
    q2_6_appropriate_analysis (str): Was an appropriate analysis used to estimate the effect of assignment to intervention?
    q2_7_substantial_impact (str): If N/PN/NI to 2.6: Was there substantial impact on the result due to failure to analyse participants in the group to which they were randomized?
    
    Response options for all questions: 'Y', 'PY', 'PN', 'N', 'NI', 'NA'
    
    Returns:
    tuple: (risk_level, part1_risk, part2_risk, reasoning)
    """
    
    # Normalize inputs
    q2_1 = q2_1_participants_aware.upper()
    q2_2 = q2_2_personnel_aware.upper()
    q2_3 = q2_3_deviations_occurred.upper()
    q2_4 = q2_4_deviations_affect_outcome.upper()
    q2_5 = q2_5_deviations_balanced.upper()
    q2_6 = q2_6_appropriate_analysis.upper()
    q2_7 = q2_7_substantial_impact.upper()
    
    # Validate inputs
    valid_responses = ['Y', 'PY', 'PN', 'N', 'NI', 'NA']
    inputs = [q2_1, q2_2, q2_3, q2_4, q2_5, q2_6, q2_7]
    if not all(inp in valid_responses for inp in inputs):
        raise ValueError("Invalid response. Use: Y, PY, PN, N, NI, or NA")
    
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
    
    return overall_risk, part1_risk, part2_risk, reasoning


def assess_part1_deviations(q2_1, q2_2, q2_3, q2_4, q2_5):
    """
    Assess Part 1: Questions 2.1 to 2.5 (Intervention fidelity)
    """
    
    # LOW RISK criteria:
    # (i) Participants, carers and people delivering the interventions were unaware of intervention groups during the trial
    # OR
    # (ii.1) Participants, carers or people delivering the interventions were aware of intervention groups during the trial
    # AND (ii.2) No deviations from intended intervention arose because of the trial context
    
    # Check if both participants and personnel were unaware
    both_unaware = (q2_1 in ['N', 'PN'] and q2_2 in ['N', 'PN'])
    
    # Check if aware but no deviations occurred
    either_aware = (q2_1 in ['Y', 'PY', 'NI'] or q2_2 in ['Y', 'PY', 'NI'])
    no_deviations = (q2_3 in ['N', 'PN'])
    
    if both_unaware:
        return 'Low', 'Both participants and personnel unaware of intervention groups'
    elif either_aware and no_deviations:
        return 'Low', 'Awareness present but no deviations from intended intervention occurred'
    
    # HIGH RISK criteria:
    # (i) Participants, carers or people delivering the interventions were aware of intervention groups during the trial
    # AND (ii) There were deviations from intended interventions that arose because of the trial context
    # AND (iii) These deviations were likely to have affected the outcome
    # AND (iv) These deviations were unbalanced between the intervention groups
    
    if (either_aware and 
        q2_3 in ['Y', 'PY'] and 
        q2_4 in ['Y', 'PY', 'NI'] and 
        q2_5 in ['N', 'PN', 'NI']):
        return 'High', 'Awareness led to outcome-affecting deviations that were unbalanced between groups'
    
    # SOME CONCERNS - all other scenarios
    # This includes cases where:
    # - There's no information about deviations
    # - Deviations occurred but were not likely to affect outcome or were balanced
    # - Various intermediate scenarios
    
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
    """
    Assess Part 2: Questions 2.6 and 2.7 (Analysis approach)
    """
    
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


def detailed_assessment_domain2(q2_1, q2_2, q2_3, q2_4, q2_5, q2_6, q2_7, study_info=""):
    """
    Provides detailed assessment with all signaling questions and recommendations
    """
    overall_risk, part1_risk, part2_risk, reasoning = assess_deviations_bias(
        q2_1, q2_2, q2_3, q2_4, q2_5, q2_6, q2_7)
    
    print("=== RoB 2 Domain 2: Bias due to deviations from intended interventions ===")
    print("(Effect of assignment to intervention)")
    if study_info:
        print(f"Study: {study_info}")
    print()
    
    print("PART 1: Intervention Fidelity (Questions 2.1-2.5)")
    print(f"2.1 Were participants aware of their assigned intervention? {q2_1}")
    print(f"2.2 Were carers/personnel aware of assigned interventions? {q2_2}")
    if q2_1 in ['Y', 'PY', 'NI'] or q2_2 in ['Y', 'PY', 'NI']:
        print(f"2.3 Were there deviations from intended intervention due to trial context? {q2_3}")
        if q2_3 in ['Y', 'PY']:
            print(f"2.4 Were these deviations likely to have affected the outcome? {q2_4}")
            if q2_4 in ['Y', 'PY', 'NI']:
                print(f"2.5 Were these deviations balanced between groups? {q2_5}")
    print(f"Part 1 Assessment: {part1_risk}")
    print()
    
    print("PART 2: Analysis Approach (Questions 2.6-2.7)")
    print(f"2.6 Was appropriate analysis used to estimate effect of assignment? {q2_6}")
    if q2_6 in ['N', 'PN', 'NI']:
        print(f"2.7 Was there substantial impact due to failure to analyse participants in randomized groups? {q2_7}")
    print(f"Part 2 Assessment: {part2_risk}")
    print()
    
    print(f"OVERALL DOMAIN ASSESSMENT: {overall_risk}")
    print(f"Reasoning: {reasoning}")
    print()
    
    # Guidance based on risk level
    if overall_risk == "Low":
        print("✓ This domain poses low risk of bias")
        print("Both intervention fidelity and analysis approach are appropriate")
    elif overall_risk == "Some concerns":
        print("⚠ This domain raises some concerns")
        if part1_risk == 'Some concerns':
            print("- Consider impact of awareness/deviations on study validity")
        if part2_risk == 'Some concerns':
            print("- Consider impact of analysis approach on effect estimates")
    else:  # High risk
        print("⚠ This domain poses high risk of bias")
        print("Results should be interpreted with significant caution")
        if part1_risk == 'High':
            print("- Major concerns about intervention fidelity and differential care")
        if part2_risk == 'High':
            print("- Major concerns about analysis approach affecting effect estimates")
    
    return overall_risk, part1_risk, part2_risk, reasoning


# Example usage and test cases
if __name__ == "__main__":
    print("Testing RoB 2 Domain 2 Assessment Algorithm\n")
    
    # Test case 1: Low risk - double blind with appropriate analysis
    print("Test 1 - Low Risk (Double-blind with ITT analysis):")
    detailed_assessment_domain2('N', 'N', 'NA', 'NA', 'NA', 'Y', 'NA', 
                              "Double-blind RCT with ITT analysis")
    print("-" * 80)
    
    # Test case 2: Some concerns - open label but no deviations
    print("Test 2 - Some Concerns (Open-label, no deviations):")
    detailed_assessment_domain2('Y', 'Y', 'N', 'NA', 'NA', 'Y', 'NA',
                              "Open-label RCT with no reported deviations")
    print("-" * 80)
    
    # Test case 3: High risk - deviations affecting outcome, unbalanced
    print("Test 3 - High Risk (Unbalanced outcome-affecting deviations):")
    detailed_assessment_domain2('Y', 'Y', 'Y', 'Y', 'N', 'Y', 'NA',
                              "Open-label RCT with differential care")
    print("-" * 80)
    
    # Test case 4: High risk - inappropriate analysis with impact
    print("Test 4 - High Risk (Per-protocol analysis with substantial impact):")
    detailed_assessment_domain2('N', 'N', 'NA', 'NA', 'NA', 'N', 'Y',
                              "RCT with per-protocol analysis excluding many participants")
    print("-" * 80)
    
    # Test case 5: Some concerns - balanced deviations
    print("Test 5 - Some Concerns (Balanced deviations):")
    detailed_assessment_domain2('Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'NA',
                              "Open-label RCT with balanced co-interventions")
