"""
ROBINS-E Tool Domain 6: Risk of Bias due to Measurement of Outcomes
Implementation of the algorithm for assessing bias in outcome measurement
"""

from enum import Enum
from typing import Dict, Any

class Response(Enum):
    """Possible responses to algorithm questions"""
    YES = "Y"
    PROBABLY_YES = "PY"
    NO = "N"
    PROBABLY_NO = "PN"
    NO_INFORMATION = "NI"
    STRONG_YES = "SY"
    WEAK_YES = "WY"

class RiskLevel(Enum):
    """Risk of bias levels"""
    LOW_RISK = "Low risk of bias"
    SOME_CONCERNS = "Some concerns"
    HIGH_RISK = "High risk of bias"

class ROBINSEDomain6:
    """ROBINS-E Domain 6 Algorithm Implementation"""
    
    def __init__(self):
        self.questions = {
            'q6_1_measurement_differs': "6.1 Measurement of outcome differs by exposure?",
            'q6_2_assessors_aware': "6.2 Outcome assessors aware of exposure history?",
            'q6_3_assessment_influenced': "6.3 Assessment could be influenced by knowledge of exposure?"
        }
    
    def _is_positive_response(self, response: Response) -> bool:
        """Check if response is positive (Y/PY)"""
        return response in [Response.YES, Response.PROBABLY_YES]
    
    def _is_negative_response(self, response: Response) -> bool:
        """Check if response is negative (N/PN)"""
        return response in [Response.NO, Response.PROBABLY_NO]
    
    def _is_positive_or_ni(self, response: Response) -> bool:
        """Check if response is positive or no information (Y/PY/NI)"""
        return response in [Response.YES, Response.PROBABLY_YES, Response.NO_INFORMATION]
    
    def _is_weak_yes_or_ni(self, response: Response) -> bool:
        """Check if response is weak yes or no information (WY/NI)"""
        return response in [Response.WEAK_YES, Response.NO_INFORMATION]
    
    def _is_strong_yes(self, response: Response) -> bool:
        """Check if response is strong yes (SY)"""
        return response == Response.STRONG_YES

    def assess_outcome_measurement_bias(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Assess risk of bias due to measurement of outcomes
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with risk assessment and pathway taken
        """
        pathway = []
        
        # Start with Q6.1 Measurement of outcome differs by exposure?
        q6_1 = responses.get('q6_1_measurement_differs')
        if not q6_1:
            return {
                'risk_level': RiskLevel.SOME_CONCERNS,
                'pathway': ["Missing Q6.1 response"],
                'rationale': 'incomplete_measurement_assessment'
            }
        
        pathway.append(f"Q6.1 Measurement of outcome differs by exposure? -> {q6_1.value}")
        
        # Direct path to HIGH RISK for differential measurement
        if self._is_positive_response(q6_1):
            pathway.append("Y/PY path -> HIGH RISK OF BIAS")
            return {
                'risk_level': RiskLevel.HIGH_RISK,
                'pathway': pathway,
                'rationale': 'differential_outcome_measurement'
            }
        
        # N/PN and NI paths both proceed to Q6.2
        if self._is_negative_response(q6_1) or q6_1 == Response.NO_INFORMATION:
            if self._is_negative_response(q6_1):
                pathway.append("N/PN path -> Proceeding to Q6.2")
            else:
                pathway.append("NI path -> Proceeding to Q6.2")
            
            q6_2 = responses.get('q6_2_assessors_aware')
            if not q6_2:
                return {
                    'risk_level': RiskLevel.SOME_CONCERNS,
                    'pathway': pathway + ["Missing Q6.2 response"],
                    'rationale': 'incomplete_awareness_assessment'
                }
            
            pathway.append(f"Q6.2 Outcome assessors aware of exposure history? -> {q6_2.value}")
            
            # Direct path to LOW RISK if assessors unaware
            if self._is_negative_response(q6_2):
                pathway.append("N/PN path -> LOW RISK OF BIAS")
                return {
                    'risk_level': RiskLevel.LOW_RISK,
                    'pathway': pathway,
                    'rationale': 'assessors_unaware_of_exposure'
                }
            
            # Y/PY/NI paths proceed to Q6.3
            if self._is_positive_or_ni(q6_2):
                if self._is_positive_response(q6_2):
                    pathway.append("Y/PY path -> Proceeding to Q6.3")
                else:
                    pathway.append("NI path -> Proceeding to Q6.3")
                
                q6_3 = responses.get('q6_3_assessment_influenced')
                if not q6_3:
                    return {
                        'risk_level': RiskLevel.HIGH_RISK,
                        'pathway': pathway + ["Missing Q6.3 response -> HIGH RISK"],
                        'rationale': 'incomplete_influence_assessment'
                    }
                
                pathway.append(f"Q6.3 Assessment could be influenced by knowledge of exposure? -> {q6_3.value}")
                
                # Assess influence potential
                if self._is_negative_response(q6_3):
                    pathway.append("N/PN path -> LOW RISK OF BIAS")
                    return {
                        'risk_level': RiskLevel.LOW_RISK,
                        'pathway': pathway,
                        'rationale': 'assessors_aware_but_not_influenced'
                    }
                
                elif self._is_weak_yes_or_ni(q6_3):
                    pathway.append("WY/NI path -> SOME CONCERNS")
                    return {
                        'risk_level': RiskLevel.SOME_CONCERNS,
                        'pathway': pathway,
                        'rationale': 'possible_assessment_influence'
                    }
                
                elif self._is_strong_yes(q6_3):
                    pathway.append("SY path -> HIGH RISK OF BIAS")
                    return {
                        'risk_level': RiskLevel.HIGH_RISK,
                        'pathway': pathway,
                        'rationale': 'strong_assessment_influence'
                    }
        
        # Default fallback (should not reach here with valid inputs)
        return {
            'risk_level': RiskLevel.SOME_CONCERNS,
            'pathway': pathway + ["Unexpected pathway - defaulting to SOME CONCERNS"],
            'rationale': 'unexpected_case'
        }

    def get_detailed_assessment(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Get detailed assessment with additional context about outcome measurement
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with detailed risk assessment and explanations
        """
        result = self.assess_outcome_measurement_bias(responses)
        
        # Add detailed explanations based on rationale
        explanations = {
            'differential_outcome_measurement': 
                "Outcome measurement methods differed between exposure groups, creating "
                "systematic bias in outcome assessment. This represents a fundamental flaw "
                "that cannot be adequately corrected analytically.",
            
            'assessors_unaware_of_exposure': 
                "Outcome assessors were unaware of participants' exposure history, eliminating "
                "the potential for assessment bias. This represents optimal blinding conditions.",
            
            'assessors_aware_but_not_influenced': 
                "While outcome assessors were aware of exposure history, the assessment "
                "process was unlikely to be influenced by this knowledge, maintaining objectivity.",
            
            'possible_assessment_influence': 
                "Outcome assessors were aware of exposure history and this knowledge could "
                "potentially influence their assessments, introducing some bias risk.",
            
            'strong_assessment_influence': 
                "Outcome assessors were aware of exposure history and this knowledge was "
                "likely to strongly influence their assessments, creating substantial bias.",
            
            'incomplete_measurement_assessment': 
                "Insufficient information to assess whether outcome measurement differed by exposure.",
            
            'incomplete_awareness_assessment': 
                "Insufficient information to assess outcome assessor awareness of exposure.",
            
            'incomplete_influence_assessment': 
                "Cannot determine if assessment could be influenced by exposure knowledge."
        }
        
        result['explanation'] = explanations.get(
            result['rationale'], 
            f"Assessment based on: {result['rationale']}"
        )
        
        # Add blinding assessment
        blinding_status = self._assess_blinding_status(responses)
        result['blinding_status'] = blinding_status
        
        # Add bias mechanism assessment
        bias_mechanism = self._assess_bias_mechanism(responses)
        result['bias_mechanism'] = bias_mechanism
        
        return result

    def _assess_blinding_status(self, responses: Dict[str, Response]) -> str:
        """Assess the blinding status of outcome assessment"""
        q6_1 = responses.get('q6_1_measurement_differs')
        q6_2 = responses.get('q6_2_assessors_aware')
        
        if q6_1 and self._is_positive_response(q6_1):
            return "No blinding - differential measurement methods"
        
        if q6_2:
            if self._is_negative_response(q6_2):
                return "Effective blinding - assessors unaware of exposure"
            elif self._is_positive_response(q6_2):
                return "No blinding - assessors aware of exposure"
            elif q6_2 == Response.NO_INFORMATION:
                return "Blinding status unclear"
        
        return "Insufficient information to assess blinding"

    def _assess_bias_mechanism(self, responses: Dict[str, Response]) -> str:
        """Assess the primary mechanism of potential bias"""
        q6_1 = responses.get('q6_1_measurement_differs')
        q6_3 = responses.get('q6_3_assessment_influenced')
        
        if q6_1 and self._is_positive_response(q6_1):
            return "Systematic measurement differences between exposure groups"
        
        if q6_3:
            if self._is_strong_yes(q6_3):
                return "Strong potential for assessor bias due to exposure knowledge"
            elif self._is_weak_yes_or_ni(q6_3):
                return "Moderate potential for assessor bias"
            elif self._is_negative_response(q6_3):
                return "Minimal potential for assessor bias"
        
        return "Bias mechanism unclear"

    def get_questions(self) -> Dict[str, str]:
        """Return the algorithm questions"""
        return self.questions.copy()

    def validate_responses(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Validate that provided responses are complete and follow logical flow
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'missing_questions': [],
            'logical_inconsistencies': [],
            'recommendations': []
        }
        
        # Check Q6.1
        if 'q6_1_measurement_differs' not in responses:
            validation['is_valid'] = False
            validation['missing_questions'].append('q6_1_measurement_differs')
        else:
            q6_1 = responses['q6_1_measurement_differs']
            
            # If Q6.1 is Y/PY, no further questions needed
            if self._is_positive_response(q6_1):
                # Check if unnecessary questions were answered
                if 'q6_2_assessors_aware' in responses or 'q6_3_assessment_influenced' in responses:
                    validation['recommendations'].append(
                        "Q6.2 and Q6.3 not needed when Q6.1 is Y/PY (differential measurement)"
                    )
            else:
                # Q6.2 is needed
                if 'q6_2_assessors_aware' not in responses:
                    validation['is_valid'] = False
                    validation['missing_questions'].append('q6_2_assessors_aware')
                else:
                    q6_2 = responses['q6_2_assessors_aware']
                    
                    # If Q6.2 is N/PN, Q6.3 not needed
                    if self._is_negative_response(q6_2):
                        if 'q6_3_assessment_influenced' in responses:
                            validation['recommendations'].append(
                                "Q6.3 not needed when Q6.2 is N/PN (assessors unaware)"
                            )
                    else:
                        # Q6.3 is needed
                        if 'q6_3_assessment_influenced' not in responses:
                            validation['is_valid'] = False
                            validation['missing_questions'].append('q6_3_assessment_influenced')
        
        return validation

# Example usage and testing
if __name__ == "__main__":
    robins_e_d6 = ROBINSEDomain6()
    
    # Example 1: Low risk - assessors unaware
    responses_low = {
        'q6_1_measurement_differs': Response.NO,
        'q6_2_assessors_aware': Response.NO
    }
    
    result_low = robins_e_d6.get_detailed_assessment(responses_low)
    print("=== Low Risk Example ===")
    print(f"Risk Level: {result_low['risk_level'].value}")
    print(f"Rationale: {result_low['rationale']}")
    print(f"Blinding Status: {result_low['blinding_status']}")
    print(f"Bias Mechanism: {result_low['bias_mechanism']}")
    print(f"Explanation: {result_low['explanation']}")
    print()
    
    # Example 2: Some concerns - possible influence
    responses_concerns = {
        'q6_1_measurement_differs': Response.NO,
        'q6_2_assessors_aware': Response.YES,
        'q6_3_assessment_influenced': Response.WEAK_YES
    }
    
    result_concerns = robins_e_d6.get_detailed_assessment(responses_concerns)
    print("=== Some Concerns Example ===")
    print(f"Risk Level: {result_concerns['risk_level'].value}")
    print(f"Rationale: {result_concerns['rationale']}")
    print(f"Blinding Status: {result_concerns['blinding_status']}")
    print(f"Bias Mechanism: {result_concerns['bias_mechanism']}")
    print(f"Explanation: {result_concerns['explanation']}")
    print()
    
    # Example 3: High risk - differential measurement
    responses_high_diff = {
        'q6_1_measurement_differs': Response.YES
    }
    
    result_high_diff = robins_e_d6.get_detailed_assessment(responses_high_diff)
    print("=== High Risk (Differential Measurement) Example ===")
    print(f"Risk Level: {result_high_diff['risk_level'].value}")
    print(f"Rationale: {result_high_diff['rationale']}")
    print(f"Blinding Status: {result_high_diff['blinding_status']}")
    print(f"Bias Mechanism: {result_high_diff['bias_mechanism']}")
    print(f"Explanation: {result_high_diff['explanation']}")
    print()
    
    # Example 4: High risk - strong influence
    responses_high_influence = {
        'q6_1_measurement_differs': Response.NO,
        'q6_2_assessors_aware': Response.YES,
        'q6_3_assessment_influenced': Response.STRONG_YES
    }
    
    result_high_influence = robins_e_d6.get_detailed_assessment(responses_high_influence)
    print("=== High Risk (Strong Influence) Example ===")
    print(f"Risk Level: {result_high_influence['risk_level'].value}")
    print(f"Rationale: {result_high_influence['rationale']}")
    print(f"Blinding Status: {result_high_influence['blinding_status']}")
    print(f"Bias Mechanism: {result_high_influence['bias_mechanism']}")
    print(f"Explanation: {result_high_influence['explanation']}")
    print()
    
    # Example 5: Validation check
    incomplete_responses = {
        'q6_1_measurement_differs': Response.NO,
        'q6_2_assessors_aware': Response.YES
        # Missing Q6.3
    }
    
    validation = robins_e_d6.validate_responses(incomplete_responses)
    print("=== Validation Example ===")
    print(f"Is Valid: {validation['is_valid']}")
    print(f"Missing Questions: {validation['missing_questions']}")
    print(f"Recommendations: {validation['recommendations']}")
    print()
    
    # Print available questions for reference
    print("=== Available Questions ===")
    for key, question in robins_e_d6.get_questions().items():
        print(f"{key}: {question}")
