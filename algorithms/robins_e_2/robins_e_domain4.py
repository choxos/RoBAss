"""
ROBINS-E Tool Domain 4: Risk of Bias due to Post-Exposure Interventions
Implementation of the algorithm for assessing bias from interventions after exposure
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

class RiskLevel(Enum):
    """Risk of bias levels"""
    LOW_RISK = "Low risk of bias"
    SOME_CONCERNS = "Some concerns"
    HIGH_RISK = "High risk of bias"

class ROBINSEDomain4:
    """ROBINS-E Domain 4 Algorithm Implementation"""
    
    def __init__(self):
        self.questions = {
            'q4_1_post_exposure_interventions': "4.1 Were there post-exposure interventions influenced by exposure?",
            'q4_2_analysis_corrected': "4.2 Likely that analysis corrected for effect of these?"
        }
    
    def _is_positive_response(self, response: Response) -> bool:
        """Check if response is positive (Y/PY)"""
        return response in [Response.YES, Response.PROBABLY_YES]
    
    def _is_negative_response(self, response: Response) -> bool:
        """Check if response is negative (N/PN)"""
        return response in [Response.NO, Response.PROBABLY_NO]
    
    def _is_no_information(self, response: Response) -> bool:
        """Check if response is no information (NI)"""
        return response == Response.NO_INFORMATION
    
    def _is_negative_or_ni(self, response: Response) -> bool:
        """Check if response is negative or no information (N/PN/NI)"""
        return response in [Response.NO, Response.PROBABLY_NO, Response.NO_INFORMATION]

    def assess_post_exposure_interventions_bias(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Assess risk of bias due to post-exposure interventions
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with risk assessment and pathway taken
        """
        pathway = []
        
        # Start with Q4.1 Were there post-exposure interventions influenced by exposure?
        q4_1 = responses.get('q4_1_post_exposure_interventions')
        if not q4_1:
            return {
                'risk_level': RiskLevel.SOME_CONCERNS,
                'pathway': ["Missing Q4.1 response"],
                'rationale': 'incomplete_data'
            }
        
        pathway.append(f"Q4.1 Were there post-exposure interventions influenced by exposure? -> {q4_1.value}")
        
        # Handle direct path to LOW RISK
        if self._is_negative_response(q4_1):
            pathway.append("N/PN path -> LOW RISK OF BIAS")
            return {
                'risk_level': RiskLevel.LOW_RISK,
                'pathway': pathway,
                'rationale': 'no_post_exposure_interventions'
            }
        
        # Handle Y/PY and NI paths - both go to Q4.2
        if self._is_positive_response(q4_1) or self._is_no_information(q4_1):
            if self._is_positive_response(q4_1):
                pathway.append("Y/PY path -> Proceeding to Q4.2")
            else:
                pathway.append("NI path -> Proceeding to Q4.2")
            
            q4_2 = responses.get('q4_2_analysis_corrected')
            if not q4_2:
                return {
                    'risk_level': RiskLevel.HIGH_RISK,
                    'pathway': pathway + ["Missing Q4.2 response -> HIGH RISK"],
                    'rationale': 'incomplete_correction_assessment'
                }
            
            pathway.append(f"Q4.2 Likely that analysis corrected for effect of these? -> {q4_2.value}")
            
            # Assess correction adequacy
            if self._is_positive_response(q4_2):
                pathway.append("Y/PY path -> SOME CONCERNS")
                return {
                    'risk_level': RiskLevel.SOME_CONCERNS,
                    'pathway': pathway,
                    'rationale': 'interventions_present_but_corrected'
                }
            
            elif self._is_negative_or_ni(q4_2):
                pathway.append("N/PN/NI path -> HIGH RISK OF BIAS")
                return {
                    'risk_level': RiskLevel.HIGH_RISK,
                    'pathway': pathway,
                    'rationale': 'interventions_present_not_corrected'
                }
        
        # Default fallback (should not reach here with valid inputs)
        return {
            'risk_level': RiskLevel.SOME_CONCERNS,
            'pathway': pathway + ["Unexpected pathway - defaulting to SOME CONCERNS"],
            'rationale': 'unexpected_case'
        }

    def get_detailed_assessment(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Get detailed assessment with additional context
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with detailed risk assessment and explanations
        """
        result = self.assess_post_exposure_interventions_bias(responses)
        
        # Add detailed explanations based on the rationale
        explanations = {
            'no_post_exposure_interventions': 
                "No post-exposure interventions influenced by exposure were identified. "
                "This eliminates a major source of bias in observational studies.",
            
            'interventions_present_but_corrected': 
                "Post-exposure interventions influenced by exposure were present, but the analysis "
                "likely corrected for their effects. Some residual bias may remain.",
            
            'interventions_present_not_corrected': 
                "Post-exposure interventions influenced by exposure were present, and the analysis "
                "did not adequately correct for their effects. This creates substantial bias risk.",
            
            'incomplete_correction_assessment': 
                "Post-exposure interventions may be present, but assessment of analytical "
                "corrections is incomplete. High risk assumed as precautionary measure.",
            
            'incomplete_data': 
                "Insufficient information to assess post-exposure interventions.",
            
            'unexpected_case': 
                "Unexpected response pattern encountered in the assessment."
        }
        
        result['explanation'] = explanations.get(result['rationale'], 
                                                "No specific explanation available.")
        
        # Add intervention impact assessment
        q4_1 = responses.get('q4_1_post_exposure_interventions')
        q4_2 = responses.get('q4_2_analysis_corrected')
        
        if q4_1 and self._is_positive_response(q4_1):
            if q4_2 and self._is_positive_response(q4_2):
                result['intervention_impact'] = "Moderate - interventions present but likely controlled"
            elif q4_2 and self._is_negative_or_ni(q4_2):
                result['intervention_impact'] = "High - interventions present and not controlled"
            else:
                result['intervention_impact'] = "Unknown - correction status unclear"
        else:
            result['intervention_impact'] = "Minimal - no significant interventions identified"
        
        return result

    def get_questions(self) -> Dict[str, str]:
        """Return the algorithm questions"""
        return self.questions.copy()

    def validate_responses(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Validate that provided responses are complete and appropriate
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'missing_questions': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check Q4.1
        if 'q4_1_post_exposure_interventions' not in responses:
            validation['is_valid'] = False
            validation['missing_questions'].append('q4_1_post_exposure_interventions')
        else:
            q4_1 = responses['q4_1_post_exposure_interventions']
            
            # Check if Q4.2 is needed
            if (self._is_positive_response(q4_1) or self._is_no_information(q4_1)):
                if 'q4_2_analysis_corrected' not in responses:
                    validation['is_valid'] = False
                    validation['missing_questions'].append('q4_2_analysis_corrected')
                    validation['recommendations'].append(
                        "Q4.2 is required when Q4.1 is Y/PY/NI"
                    )
            
            # Provide guidance based on Q4.1 response
            if self._is_positive_response(q4_1):
                validation['recommendations'].append(
                    "Consider documenting specific post-exposure interventions identified"
                )
            elif self._is_no_information(q4_1):
                validation['warnings'].append(
                    "Lack of information about post-exposure interventions may indicate "
                    "incomplete data collection"
                )
        
        return validation

# Example usage and testing
if __name__ == "__main__":
    robins_e_d4 = ROBINSEDomain4()
    
    # Example 1: Low risk scenario - no post-exposure interventions
    responses_low = {
        'q4_1_post_exposure_interventions': Response.NO
    }
    
    result_low = robins_e_d4.get_detailed_assessment(responses_low)
    print("=== Low Risk Example ===")
    print(f"Risk Level: {result_low['risk_level'].value}")
    print(f"Rationale: {result_low['rationale']}")
    print(f"Intervention Impact: {result_low['intervention_impact']}")
    print(f"Explanation: {result_low['explanation']}")
    print(f"Pathway: {' -> '.join(result_low['pathway'])}")
    print()
    
    # Example 2: Some concerns scenario - interventions present but corrected
    responses_concerns = {
        'q4_1_post_exposure_interventions': Response.YES,
        'q4_2_analysis_corrected': Response.PROBABLY_YES
    }
    
    result_concerns = robins_e_d4.get_detailed_assessment(responses_concerns)
    print("=== Some Concerns Example ===")
    print(f"Risk Level: {result_concerns['risk_level'].value}")
    print(f"Rationale: {result_concerns['rationale']}")
    print(f"Intervention Impact: {result_concerns['intervention_impact']}")
    print(f"Explanation: {result_concerns['explanation']}")
    print(f"Pathway: {' -> '.join(result_concerns['pathway'])}")
    print()
    
    # Example 3: High risk scenario - interventions present and not corrected
    responses_high = {
        'q4_1_post_exposure_interventions': Response.PROBABLY_YES,
        'q4_2_analysis_corrected': Response.NO
    }
    
    result_high = robins_e_d4.get_detailed_assessment(responses_high)
    print("=== High Risk Example ===")
    print(f"Risk Level: {result_high['risk_level'].value}")
    print(f"Rationale: {result_high['rationale']}")
    print(f"Intervention Impact: {result_high['intervention_impact']}")
    print(f"Explanation: {result_high['explanation']}")
    print(f"Pathway: {' -> '.join(result_high['pathway'])}")
    print()
    
    # Example 4: No information scenario
    responses_ni = {
        'q4_1_post_exposure_interventions': Response.NO_INFORMATION,
        'q4_2_analysis_corrected': Response.NO_INFORMATION
    }
    
    result_ni = robins_e_d4.get_detailed_assessment(responses_ni)
    print("=== No Information Example ===")
    print(f"Risk Level: {result_ni['risk_level'].value}")
    print(f"Rationale: {result_ni['rationale']}")
    print(f"Intervention Impact: {result_ni['intervention_impact']}")
    print(f"Explanation: {result_ni['explanation']}")
    print()
    
    # Example 5: Validation check
    incomplete_responses = {
        'q4_1_post_exposure_interventions': Response.YES
        # Missing Q4.2
    }
    
    validation = robins_e_d4.validate_responses(incomplete_responses)
    print("=== Validation Example ===")
    print(f"Is Valid: {validation['is_valid']}")
    print(f"Missing Questions: {validation['missing_questions']}")
    print(f"Recommendations: {validation['recommendations']}")
    print()
    
    # Print available questions for reference
    print("=== Available Questions ===")
    for key, question in robins_e_d4.get_questions().items():
        print(f"{key}: {question}")
