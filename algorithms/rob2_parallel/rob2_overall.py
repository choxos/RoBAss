def assess_overall_rob2(domain1_risk, domain2_risk, domain3_risk, domain4_risk, domain5_risk,
                       outcome_description="", assessor_override=None, 
                       override_justification=""):
    """
    RoB 2 Overall Risk of Bias Assessment
    
    Combines assessments from all five domains to reach an overall judgment
    
    Parameters:
    domain1_risk (str): Risk level for Domain 1 (Randomization process)
    domain2_risk (str): Risk level for Domain 2 (Deviations from intended interventions)
    domain3_risk (str): Risk level for Domain 3 (Missing outcome data)
    domain4_risk (str): Risk level for Domain 4 (Measurement of outcome)
    domain5_risk (str): Risk level for Domain 5 (Selection of reported result)
    outcome_description (str): Description of the specific outcome being assessed
    assessor_override (str): Optional override by assessor ('Low', 'Some concerns', 'High')
    override_justification (str): Justification for any override
    
    Returns:
    tuple: (overall_risk, reasoning, domain_summary)
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
    
    # Create domain summary
    domain_summary = {}
    for i, (domain, risk) in enumerate(zip(domain_names, risks)):
        domain_summary[f"domain_{i+1}"] = {"name": domain, "risk": risk}
    
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
    
    # Apply assessor override if provided
    if assessor_override and assessor_override in valid_risks:
        if assessor_override != overall_risk:
            original_risk = overall_risk
            overall_risk = assessor_override
            reasoning += f" [Override: Changed from '{original_risk}' to '{assessor_override}' - {override_justification}]"
    
    return overall_risk, reasoning, domain_summary


def comprehensive_rob2_assessment(study_info, outcome_description, 
                                 domain_assessments, assessor_info=""):
    """
    Complete RoB 2 assessment with detailed reporting
    
    Parameters:
    study_info (dict): Study details (title, authors, year, etc.)
    outcome_description (str): Specific outcome being assessed
    domain_assessments (dict): Results from all five domain assessments
    assessor_info (str): Information about who conducted the assessment
    
    Returns:
    dict: Complete assessment results
    """
    
    # Extract domain risks
    d1_risk = domain_assessments['domain1']['risk']
    d2_risk = domain_assessments['domain2']['risk'] 
    d3_risk = domain_assessments['domain3']['risk']
    d4_risk = domain_assessments['domain4']['risk']
    d5_risk = domain_assessments['domain5']['risk']
    
    # Get overall assessment
    overall_risk, reasoning, domain_summary = assess_overall_rob2(
        d1_risk, d2_risk, d3_risk, d4_risk, d5_risk, outcome_description)
    
    # Create comprehensive report
    print("=" * 80)
    print("RoB 2 COMPREHENSIVE ASSESSMENT")
    print("=" * 80)
    
    if study_info:
        print(f"Study: {study_info.get('title', 'Unknown')}")
        if 'authors' in study_info:
            print(f"Authors: {study_info['authors']}")
        if 'year' in study_info:
            print(f"Year: {study_info['year']}")
    
    print(f"Outcome: {outcome_description}")
    if assessor_info:
        print(f"Assessor: {assessor_info}")
    print()
    
    # Domain-by-domain summary
    print("DOMAIN-BY-DOMAIN ASSESSMENT:")
    print("-" * 50)
    
    risk_symbols = {
        'Low': '🟢',
        'Some concerns': '🟡', 
        'High': '🔴'
    }
    
    for i in range(1, 6):
        domain_key = f'domain{i}'
        domain_info = domain_summary[f'domain_{i}']
        domain_detail = domain_assessments[domain_key]
        
        symbol = risk_symbols.get(domain_info['risk'], '⚪')
        print(f"{symbol} {domain_info['name']}: {domain_info['risk']}")
        
        if 'reasoning' in domain_detail:
            print(f"   Reasoning: {domain_detail['reasoning']}")
        print()
    
    # Overall assessment
    print("OVERALL ASSESSMENT:")
    print("-" * 50)
    overall_symbol = risk_symbols.get(overall_risk, '⚪')
    print(f"{overall_symbol} OVERALL RISK OF BIAS: {overall_risk.upper()}")
    print(f"Reasoning: {reasoning}")
    print()
    
    # Interpretation and recommendations
    print("INTERPRETATION:")
    print("-" * 50)
    
    if overall_risk == 'Low':
        print("✓ This study has low risk of bias for this outcome")
        print("- Results can be interpreted with confidence")
        print("- Appropriate for inclusion in evidence synthesis")
        print("- Weight in meta-analysis: Standard weighting appropriate")
        
    elif overall_risk == 'Some concerns':
        print("⚠ This study raises some concerns about bias for this outcome")
        print("- Results should be interpreted with some caution")
        print("- Consider impact of identified concerns on findings")
        print("- Weight in meta-analysis: Consider sensitivity analysis")
        print("- May warrant investigation of potential bias impact")
        
    else:  # High risk
        print("⚠ This study has high risk of bias for this outcome")
        print("- Results should be interpreted with significant caution")
        print("- Consider exclusion from primary analysis")
        print("- Weight in meta-analysis: Consider downweighting or exclusion")
        print("- Strong candidate for sensitivity analysis")
        print("- Effect estimates may be unreliable")
    
    print()
    
    # Summary for meta-analysis
    confidence_rating = {
        'Low': 'High confidence',
        'Some concerns': 'Moderate confidence', 
        'High': 'Low confidence'
    }
    
    print("META-ANALYSIS CONSIDERATIONS:")
    print("-" * 50)
    print(f"Confidence in result: {confidence_rating[overall_risk]}")
    
    if overall_risk == 'High':
        high_domains = [name for name, risk in zip(
            ["Randomization", "Deviations", "Missing data", "Outcome measurement", "Selective reporting"],
            [d1_risk, d2_risk, d3_risk, d4_risk, d5_risk]
        ) if risk == 'High']
        print(f"Primary concerns: {', '.join(high_domains)}")
    
    return {
        'overall_risk': overall_risk,
        'reasoning': reasoning,
        'domain_summary': domain_summary,
        'study_info': study_info,
        'outcome': outcome_description,
        'confidence_rating': confidence_rating[overall_risk]
    }


def create_rob2_summary_table(multiple_assessments):
    """
    Create a summary table for multiple RoB 2 assessments
    
    Parameters:
    multiple_assessments (list): List of assessment dictionaries
    
    Returns:
    None (prints formatted table)
    """
    print("\nRoB 2 SUMMARY TABLE")
    print("=" * 120)
    
    # Header
    header = f"{'Study':<25} {'Outcome':<20} {'D1':<4} {'D2':<4} {'D3':<4} {'D4':<4} {'D5':<4} {'Overall':<15}"
    print(header)
    print("-" * 120)
    
    # Risk abbreviations
    risk_abbrev = {'Low': 'L', 'Some concerns': 'SC', 'High': 'H'}
    
    for assessment in multiple_assessments:
        study_name = assessment['study_info'].get('title', 'Unknown')[:24]
        outcome = assessment['outcome'][:19]
        
        # Get domain risks
        d1 = risk_abbrev[assessment['domain_summary']['domain_1']['risk']]
        d2 = risk_abbrev[assessment['domain_summary']['domain_2']['risk']]
        d3 = risk_abbrev[assessment['domain_summary']['domain_3']['risk']]
        d4 = risk_abbrev[assessment['domain_summary']['domain_4']['risk']]
        d5 = risk_abbrev[assessment['domain_summary']['domain_5']['risk']]
        overall = risk_abbrev[assessment['overall_risk']]
        
        row = f"{study_name:<25} {outcome:<20} {d1:<4} {d2:<4} {d3:<4} {d4:<4} {d5:<4} {overall:<15}"
        print(row)
    
    print()
    print("Legend: L = Low risk, SC = Some concerns, H = High risk")
    print("Domains: D1 = Randomization, D2 = Deviations, D3 = Missing data, D4 = Outcome measurement, D5 = Selective reporting")


# Example usage and test cases
if __name__ == "__main__":
    print("Testing RoB 2 Overall Assessment Algorithm\n")
    
    # Example study assessments
    study1_domains = {
        'domain1': {'risk': 'Low', 'reasoning': 'Adequate randomization and concealment'},
        'domain2': {'risk': 'Low', 'reasoning': 'Double-blind with ITT analysis'},
        'domain3': {'risk': 'Some concerns', 'reasoning': 'Some missing data but unlikely to affect results'},
        'domain4': {'risk': 'Low', 'reasoning': 'Objective outcome measured consistently'},
        'domain5': {'risk': 'Low', 'reasoning': 'Pre-specified analysis plan followed'}
    }
    
    study1_info = {
        'title': 'Effectiveness of Drug X vs Placebo',
        'authors': 'Smith et al.',
        'year': '2023'
    }
    
    # Test case 1: Some concerns overall
    print("Test 1 - Some Concerns Overall:")
    assessment1 = comprehensive_rob2_assessment(
        study1_info, 
        "Primary efficacy endpoint at 12 weeks",
        study1_domains,
        "Jane Doe, Research Fellow"
    )
    print("\n" + "="*80 + "\n")
    
    # Test case 2: High risk due to one high-risk domain
    study2_domains = {
        'domain1': {'risk': 'Low', 'reasoning': 'Good randomization'},
        'domain2': {'risk': 'High', 'reasoning': 'Open-label with differential care'},
        'domain3': {'risk': 'Low', 'reasoning': 'Complete data'},
        'domain4': {'risk': 'Low', 'reasoning': 'Objective outcome'},
        'domain5': {'risk': 'Low', 'reasoning': 'Pre-specified'}
    }
    
    print("Test 2 - High Risk (One High-Risk Domain):")
    assessment2 = comprehensive_rob2_assessment(
        {'title': 'Open-label RCT of Intervention Y', 'year': '2022'},
        "Safety endpoint",
        study2_domains
    )
    print("\n" + "="*80 + "\n")
    
    # Test case 3: High risk due to multiple some concerns
    study3_domains = {
        'domain1': {'risk': 'Some concerns', 'reasoning': 'Unclear randomization method'},
        'domain2': {'risk': 'Some concerns', 'reasoning': 'Some protocol deviations'},
        'domain3': {'risk': 'Some concerns', 'reasoning': 'Missing data concerns'},
        'domain4': {'risk': 'Low', 'reasoning': 'Good outcome measurement'},
        'domain5': {'risk': 'Some concerns', 'reasoning': 'Limited analysis plan details'}
    }
    
    print("Test 3 - High Risk (Multiple Some Concerns):")
    assessment3 = comprehensive_rob2_assessment(
        {'title': 'Pilot Study Z', 'year': '2021'},
        "Exploratory endpoint",
        study3_domains
    )
    print("\n" + "="*80 + "\n")
    
    # Summary table example
    print("Summary Table Example:")
    create_rob2_summary_table([assessment1, assessment2, assessment3])
