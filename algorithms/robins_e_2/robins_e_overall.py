"""
ROBINS-E Overall Assessment: Combining all domains into overall risk of bias judgment
Implementation of the algorithm for reaching overall bias assessment and conclusion threat evaluation
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from collections import Counter

class DomainRisk(Enum):
    """Risk levels for individual domains"""
    LOW_RISK = "Low risk of bias"
    SOME_CONCERNS = "Some concerns"
    HIGH_RISK = "High risk of bias"
    VERY_HIGH_RISK = "Very high risk of bias"

class OverallRisk(Enum):
    """Overall risk of bias levels"""
    LOW_RISK_EXCEPT_CONFOUNDING = "Low risk of bias except for concerns about uncontrolled confounding"
    SOME_CONCERNS = "Some concerns"
    HIGH_RISK = "High risk of bias"
    VERY_HIGH_RISK = "Very high risk of bias"

class ConclusionThreat(Enum):
    """Whether bias threatens the conclusions"""
    YES = "Yes"
    NO = "No"
    CANNOT_TELL = "Cannot tell"

class ROBINSEOverallAssessment:
    """ROBINS-E Overall Assessment Implementation"""
    
    def __init__(self):
        self.domain_names = {
            'domain_1': "Domain 1: Confounding",
            'domain_2': "Domain 2: Measurement of Exposure",
            'domain_3': "Domain 3: Selection and Timing",
            'domain_4': "Domain 4: Post-Exposure Interventions", 
            'domain_5': "Domain 5: Missing Data",
            'domain_6': "Domain 6: Measurement of Outcomes",
            'domain_7': "Domain 7: Bias in Reported Results"
        }
    
    def _normalize_risk_level(self, risk_input: Any) -> DomainRisk:
        """
        Normalize various risk level inputs to DomainRisk enum
        """
        if isinstance(risk_input, DomainRisk):
            return risk_input
        
        # Handle string inputs
        if isinstance(risk_input, str):
            risk_str = risk_input.lower().strip()
            
            if any(phrase in risk_str for phrase in ['low risk', 'low_risk']):
                return DomainRisk.LOW_RISK
            elif any(phrase in risk_str for phrase in ['some concerns', 'some_concerns']):
                return DomainRisk.SOME_CONCERNS
            elif any(phrase in risk_str for phrase in ['very high risk', 'very_high_risk']):
                return DomainRisk.VERY_HIGH_RISK
            elif any(phrase in risk_str for phrase in ['high risk', 'high_risk']):
                return DomainRisk.HIGH_RISK
        
        # Handle enum-like objects with value attribute
        if hasattr(risk_input, 'value'):
            return self._normalize_risk_level(risk_input.value)
        
        # Default fallback
        raise ValueError(f"Cannot normalize risk level: {risk_input}")

    def assess_overall_bias_risk(self, domain_assessments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess overall risk of bias by combining all domain assessments
        
        Args:
            domain_assessments: Dictionary with domain results, e.g.:
                {
                    'domain_1': DomainRisk.LOW_RISK,
                    'domain_2': DomainRisk.SOME_CONCERNS,
                    ...
                }
            
        Returns:
            Dictionary with overall risk assessment
        """
        # Validate and normalize domain assessments
        normalized_assessments = {}
        missing_domains = []
        
        for domain_key in self.domain_names.keys():
            if domain_key in domain_assessments:
                try:
                    normalized_assessments[domain_key] = self._normalize_risk_level(
                        domain_assessments[domain_key]
                    )
                except ValueError as e:
                    return {
                        'overall_risk': OverallRisk.SOME_CONCERNS,
                        'rationale': f'invalid_risk_level_for_{domain_key}',
                        'error': str(e),
                        'domain_assessments': domain_assessments
                    }
            else:
                missing_domains.append(domain_key)
        
        if missing_domains:
            return {
                'overall_risk': OverallRisk.SOME_CONCERNS,
                'rationale': 'incomplete_domain_assessments',
                'missing_domains': missing_domains,
                'domain_assessments': normalized_assessments
            }
        
        # Count risk levels across domains
        risk_counts = Counter(normalized_assessments.values())
        
        # Apply overall assessment algorithm
        overall_assessment = self._determine_overall_risk(normalized_assessments, risk_counts)
        
        return {
            'overall_risk': overall_assessment['overall_risk'],
            'rationale': overall_assessment['rationale'],
            'domain_assessments': normalized_assessments,
            'risk_counts': dict(risk_counts),
            'contributing_domains': overall_assessment.get('contributing_domains', []),
            'assessment_details': overall_assessment.get('details', {})
        }

    def _determine_overall_risk(self, domain_assessments: Dict[str, DomainRisk], 
                              risk_counts: Counter) -> Dict[str, Any]:
        """
        Determine overall risk level based on domain assessments and combination rules
        """
        # Check for Very High Risk conditions
        if risk_counts[DomainRisk.VERY_HIGH_RISK] >= 1:
            very_high_domains = [domain for domain, risk in domain_assessments.items() 
                               if risk == DomainRisk.VERY_HIGH_RISK]
            return {
                'overall_risk': OverallRisk.VERY_HIGH_RISK,
                'rationale': 'at_least_one_very_high_risk_domain',
                'contributing_domains': very_high_domains,
                'details': {'very_high_count': risk_counts[DomainRisk.VERY_HIGH_RISK]}
            }
        
        # Alternative Very High Risk: Several domains at High risk (additive judgment)
        if risk_counts[DomainRisk.HIGH_RISK] >= 3:  # Threshold for "several" - can be adjusted
            high_domains = [domain for domain, risk in domain_assessments.items() 
                          if risk == DomainRisk.HIGH_RISK]
            return {
                'overall_risk': OverallRisk.VERY_HIGH_RISK,
                'rationale': 'several_high_risk_domains_additive',
                'contributing_domains': high_domains,
                'details': {'high_count': risk_counts[DomainRisk.HIGH_RISK]}
            }
        
        # Check for High Risk conditions
        if risk_counts[DomainRisk.HIGH_RISK] >= 1:
            high_domains = [domain for domain, risk in domain_assessments.items() 
                          if risk == DomainRisk.HIGH_RISK]
            return {
                'overall_risk': OverallRisk.HIGH_RISK,
                'rationale': 'at_least_one_high_risk_domain',
                'contributing_domains': high_domains,
                'details': {'high_count': risk_counts[DomainRisk.HIGH_RISK]}
            }
        
        # Alternative High Risk: Several domains at Some concerns (additive judgment)
        if risk_counts[DomainRisk.SOME_CONCERNS] >= 4:  # Threshold for "several" - can be adjusted
            concern_domains = [domain for domain, risk in domain_assessments.items() 
                             if risk == DomainRisk.SOME_CONCERNS]
            return {
                'overall_risk': OverallRisk.HIGH_RISK,
                'rationale': 'several_some_concerns_domains_additive',
                'contributing_domains': concern_domains,
                'details': {'some_concerns_count': risk_counts[DomainRisk.SOME_CONCERNS]}
            }
        
        # Check for Some Concerns
        if risk_counts[DomainRisk.SOME_CONCERNS] >= 1:
            concern_domains = [domain for domain, risk in domain_assessments.items() 
                             if risk == DomainRisk.SOME_CONCERNS]
            return {
                'overall_risk': OverallRisk.SOME_CONCERNS,
                'rationale': 'at_least_one_some_concerns_domain',
                'contributing_domains': concern_domains,
                'details': {'some_concerns_count': risk_counts[DomainRisk.SOME_CONCERNS]}
            }
        
        # Low risk except for confounding concerns
        # This applies when Domain 1 is Low risk and all other domains are Low risk
        if (domain_assessments.get('domain_1') == DomainRisk.LOW_RISK and 
            all(risk == DomainRisk.LOW_RISK for domain, risk in domain_assessments.items() 
                if domain != 'domain_1')):
            return {
                'overall_risk': OverallRisk.LOW_RISK_EXCEPT_CONFOUNDING,
                'rationale': 'low_risk_all_domains_confounding_caveat',
                'contributing_domains': [],
                'details': {'all_low_risk': True}
            }
        
        # This shouldn't happen with valid inputs, but provides fallback
        return {
            'overall_risk': OverallRisk.SOME_CONCERNS,
            'rationale': 'unexpected_risk_combination',
            'contributing_domains': [],
            'details': {'risk_counts': dict(risk_counts)}
        }

    def assess_conclusion_threat(self, domain_threat_assessments: Dict[str, ConclusionThreat]) -> Dict[str, Any]:
        """
        Assess whether bias threatens the conclusions based on domain-specific threat assessments
        
        Args:
            domain_threat_assessments: Dictionary with threat assessments for each domain, e.g.:
                {
                    'domain_1': ConclusionThreat.NO,
                    'domain_2': ConclusionThreat.CANNOT_TELL,
                    ...
                }
            
        Returns:
            Dictionary with overall conclusion threat assessment
        """
        if not domain_threat_assessments:
            return {
                'conclusion_threat': ConclusionThreat.CANNOT_TELL,
                'rationale': 'no_threat_assessments_provided',
                'domain_threats': {}
            }
        
        # Count threat responses
        threat_counts = Counter(domain_threat_assessments.values())
        
        # Apply threat assessment algorithm
        if threat_counts[ConclusionThreat.YES] >= 1:
            # Yes in any domains -> Overall YES
            yes_domains = [domain for domain, threat in domain_threat_assessments.items() 
                          if threat == ConclusionThreat.YES]
            return {
                'conclusion_threat': ConclusionThreat.YES,
                'rationale': 'bias_threatens_conclusions_in_any_domain',
                'threatening_domains': yes_domains,
                'domain_threats': domain_threat_assessments
            }
        
        elif threat_counts[ConclusionThreat.NO] >= 1 and threat_counts[ConclusionThreat.YES] == 0:
            # No in any domains (and no Yes) -> Overall NO
            return {
                'conclusion_threat': ConclusionThreat.NO,
                'rationale': 'bias_does_not_threaten_conclusions',
                'domain_threats': domain_threat_assessments
            }
        
        else:
            # At least one Cannot tell, but no Yes -> Overall CANNOT TELL
            uncertain_domains = [domain for domain, threat in domain_threat_assessments.items() 
                                if threat == ConclusionThreat.CANNOT_TELL]
            return {
                'conclusion_threat': ConclusionThreat.CANNOT_TELL,
                'rationale': 'uncertain_threat_assessment',
                'uncertain_domains': uncertain_domains,
                'domain_threats': domain_threat_assessments
            }

    def generate_comprehensive_assessment(self, domain_assessments: Dict[str, Any], 
                                        domain_threat_assessments: Optional[Dict[str, ConclusionThreat]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive ROBINS-E assessment including both overall risk and conclusion threat
        
        Args:
            domain_assessments: Risk assessments for all domains
            domain_threat_assessments: Optional threat assessments for all domains
            
        Returns:
            Comprehensive assessment dictionary
        """
        # Get overall bias risk assessment
        bias_assessment = self.assess_overall_bias_risk(domain_assessments)
        
        # Get conclusion threat assessment if provided
        threat_assessment = None
        if domain_threat_assessments:
            threat_assessment = self.assess_conclusion_threat(domain_threat_assessments)
        
        # Generate detailed explanation
        explanation = self._generate_explanation(bias_assessment, threat_assessment)
        
        return {
            'overall_bias_assessment': bias_assessment,
            'conclusion_threat_assessment': threat_assessment,
            'explanation': explanation,
            'recommendations': self._generate_recommendations(bias_assessment, threat_assessment)
        }

    def _generate_explanation(self, bias_assessment: Dict[str, Any], 
                            threat_assessment: Optional[Dict[str, Any]]) -> str:
        """Generate human-readable explanation of the assessment"""
        overall_risk = bias_assessment['overall_risk']
        rationale = bias_assessment['rationale']
        
        explanations = {
            'low_risk_all_domains_confounding_caveat': 
                "The study shows low risk of bias across all domains. However, as with all observational studies, "
                "there remains the possibility of uncontrolled confounding that has not been adequately addressed.",
            
            'at_least_one_some_concerns_domain': 
                "The study has some concerns about bias, with at least one domain showing potential issues, "
                "but no domains have high or very high risk of bias.",
            
            'at_least_one_high_risk_domain': 
                "The study has important problems with at least one domain showing high risk of bias, "
                "which could substantially affect the reliability of the results.",
            
            'several_some_concerns_domains_additive': 
                "While individual domains show only some concerns, the cumulative effect of multiple domains "
                "with potential bias issues elevates the overall assessment to high risk.",
            
            'at_least_one_very_high_risk_domain': 
                "The study has very serious problems with at least one domain showing very high risk of bias, "
                "which severely undermines confidence in the results.",
            
            'several_high_risk_domains_additive': 
                "Multiple domains show high risk of bias, and the cumulative effect of these problems "
                "elevates the overall assessment to very high risk."
        }
        
        explanation = explanations.get(rationale, f"Assessment based on: {rationale}")
        
        if threat_assessment:
            threat_result = threat_assessment['conclusion_threat']
            if threat_result == ConclusionThreat.YES:
                explanation += " The identified biases are likely to threaten the validity of the study conclusions."
            elif threat_result == ConclusionThreat.NO:
                explanation += " Despite the identified bias concerns, they are unlikely to threaten the main study conclusions."
            else:
                explanation += " It is unclear whether the identified biases threaten the study conclusions."
        
        return explanation

    def _generate_recommendations(self, bias_assessment: Dict[str, Any], 
                                threat_assessment: Optional[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on the assessment"""
        recommendations = []
        overall_risk = bias_assessment['overall_risk']
        
        if overall_risk == OverallRisk.LOW_RISK_EXCEPT_CONFOUNDING:
            recommendations.extend([
                "Consider additional sensitivity analyses to address potential unmeasured confounding",
                "Discuss the potential impact of residual confounding in limitations",
                "Results can be interpreted with moderate confidence"
            ])
        
        elif overall_risk == OverallRisk.SOME_CONCERNS:
            recommendations.extend([
                "Address the identified bias concerns in study interpretation",
                "Consider additional analyses to assess bias impact",
                "Results should be interpreted with caution"
            ])
        
        elif overall_risk == OverallRisk.HIGH_RISK:
            recommendations.extend([
                "Substantial bias concerns require careful interpretation",
                "Consider whether results are reliable enough for decision-making",
                "Additional studies with better methodology may be needed"
            ])
        
        elif overall_risk == OverallRisk.VERY_HIGH_RISK:
            recommendations.extend([
                "Very serious bias concerns severely limit result reliability",
                "Results should not be used for decision-making without major caveats",
                "New studies with improved methodology are strongly recommended"
            ])
        
        # Add domain-specific recommendations
        if 'contributing_domains' in bias_assessment:
            for domain in bias_assessment['contributing_domains']:
                domain_name = self.domain_names.get(domain, domain)
                recommendations.append(f"Address specific issues in {domain_name}")
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    robins_e_overall = ROBINSEOverallAssessment()
    
    # Example 1: Low risk except confounding
    domain_assessments_low = {
        'domain_1': DomainRisk.LOW_RISK,
        'domain_2': DomainRisk.LOW_RISK,
        'domain_3': DomainRisk.LOW_RISK,
        'domain_4': DomainRisk.LOW_RISK,
        'domain_5': DomainRisk.LOW_RISK,
        'domain_6': DomainRisk.LOW_RISK,
        'domain_7': DomainRisk.LOW_RISK
    }
    
    result_low = robins_e_overall.generate_comprehensive_assessment(domain_assessments_low)
    print("=== Low Risk Except Confounding Example ===")
    print(f"Overall Risk: {result_low['overall_bias_assessment']['overall_risk'].value}")
    print(f"Rationale: {result_low['overall_bias_assessment']['rationale']}")
    print(f"Explanation: {result_low['explanation']}")
    print()
    
    # Example 2: Some concerns
    domain_assessments_concerns = {
        'domain_1': DomainRisk.LOW_RISK,
        'domain_2': DomainRisk.SOME_CONCERNS,
        'domain_3': DomainRisk.LOW_RISK,
        'domain_4': DomainRisk.LOW_RISK,
        'domain_5': DomainRisk.SOME_CONCERNS,
        'domain_6': DomainRisk.LOW_RISK,
        'domain_7': DomainRisk.LOW_RISK
    }
    
    result_concerns = robins_e_overall.generate_comprehensive_assessment(domain_assessments_concerns)
    print("=== Some Concerns Example ===")
    print(f"Overall Risk: {result_concerns['overall_bias_assessment']['overall_risk'].value}")
    print(f"Contributing Domains: {result_concerns['overall_bias_assessment']['contributing_domains']}")
    print(f"Risk Counts: {result_concerns['overall_bias_assessment']['risk_counts']}")
    print()
    
    # Example 3: High risk - single high risk domain
    domain_assessments_high = {
        'domain_1': DomainRisk.LOW_RISK,
        'domain_2': DomainRisk.HIGH_RISK,
        'domain_3': DomainRisk.SOME_CONCERNS,
        'domain_4': DomainRisk.LOW_RISK,
        'domain_5': DomainRisk.LOW_RISK,
        'domain_6': DomainRisk.LOW_RISK,
        'domain_7': DomainRisk.LOW_RISK
    }
    
    result_high = robins_e_overall.generate_comprehensive_assessment(domain_assessments_high)
    print("=== High Risk (Single Domain) Example ===")
    print(f"Overall Risk: {result_high['overall_bias_assessment']['overall_risk'].value}")
    print(f"Contributing Domains: {result_high['overall_bias_assessment']['contributing_domains']}")
    print()
    
    # Example 4: Very high risk - multiple high risk domains
    domain_assessments_very_high = {
        'domain_1': DomainRisk.HIGH_RISK,
        'domain_2': DomainRisk.HIGH_RISK,
        'domain_3': DomainRisk.HIGH_RISK,
        'domain_4': DomainRisk.SOME_CONCERNS,
        'domain_5': DomainRisk.LOW_RISK,
        'domain_6': DomainRisk.LOW_RISK,
        'domain_7': DomainRisk.LOW_RISK
    }
    
    result_very_high = robins_e_overall.generate_comprehensive_assessment(domain_assessments_very_high)
    print("=== Very High Risk (Additive) Example ===")
    print(f"Overall Risk: {result_very_high['overall_bias_assessment']['overall_risk'].value}")
    print(f"Rationale: {result_very_high['overall_bias_assessment']['rationale']}")
    print(f"Contributing Domains: {result_very_high['overall_bias_assessment']['contributing_domains']}")
    print()
    
    # Example 5: With conclusion threat assessment
    domain_threat_assessments = {
        'domain_1': ConclusionThreat.NO,
        'domain_2': ConclusionThreat.YES,
        'domain_3': ConclusionThreat.CANNOT_TELL,
        'domain_4': ConclusionThreat.NO,
        'domain_5': ConclusionThreat.NO,
        'domain_6': ConclusionThreat.NO,
        'domain_7': ConclusionThreat.NO
    }
    
    result_with_threat = robins_e_overall.generate_comprehensive_assessment(
        domain_assessments_concerns, domain_threat_assessments
    )
    print("=== With Conclusion Threat Assessment ===")
    print(f"Overall Risk: {result_with_threat['overall_bias_assessment']['overall_risk'].value}")
    print(f"Conclusion Threat: {result_with_threat['conclusion_threat_assessment']['conclusion_threat'].value}")
    print(f"Threatening Domains: {result_with_threat['conclusion_threat_assessment'].get('threatening_domains', [])}")
    print(f"Explanation: {result_with_threat['explanation']}")
    print()
    
    # Example 6: Using string inputs (compatibility with domain implementations)
    domain_assessments_strings = {
        'domain_1': "Low risk of bias",
        'domain_2': "Some concerns", 
        'domain_3': "High risk of bias",
        'domain_4': "Low risk of bias",
        'domain_5': "Low risk of bias",
        'domain_6': "Low risk of bias",
        'domain_7': "Low risk of bias"
    }
    
    result_strings = robins_e_overall.assess_overall_bias_risk(domain_assessments_strings)
    print("=== String Input Example ===")
    print(f"Overall Risk: {result_strings['overall_risk'].value}")
    print(f"Rationale: {result_strings['rationale']}")
    print()
