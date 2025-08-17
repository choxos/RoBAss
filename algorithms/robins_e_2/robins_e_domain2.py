"""
ROBINS-E Tool Domain 2: Risk of Bias due to Measurement of Exposure
Implementation for all three variants (same algorithm applies to all)
"""

from enum import Enum
from typing import Dict, Any, Optional

class Response(Enum):
    """Possible responses to algorithm questions"""
    YES = "Y"
    PROBABLY_YES = "PY"
    NO = "N"
    PROBABLY_NO = "PN"
    NO_INFORMATION = "NI"
    STRONG_NO = "SN"
    WEAK_NO = "WN"
    STRONG_YES = "SY"
    WEAK_YES = "WY"

class BiasLevel(Enum):
    """Bias severity levels"""
    LOW = "Low"
    SOME = "Some" 
    HIGH = "High"

class RiskLevel(Enum):
    """Risk of bias levels"""
    LOW_RISK = "Low risk of bias"
    SOME_CONCERNS = "Some concerns"
    HIGH_RISK = "High risk of bias"
    VERY_HIGH_RISK = "Very high risk of bias"

class ROBINSEDomain2:
    """ROBINS-E Domain 2 Algorithm Implementation"""
    
    def __init__(self):
        self.questions = {
            'q2_1_exposure_characterise': "2.1 Exposure measures well characterise exposure of interest?",
            'q2_2_error_single_timepoint': "2.2 Error in measurement at a single time point?",
            'q2_3_measurement_differential': "2.3 Measurement error differential?",
            'q2_4_non_differential_error': "2.4 Important non-differential error?"
        }
    
    def _is_positive_response(self, response: Response) -> bool:
        """Check if response is positive (Y/PY)"""
        return response in [Response.YES, Response.PROBABLY_YES]
    
    def _is_negative_response(self, response: Response) -> bool:
        """Check if response is negative (N/PN)"""
        return response in [Response.NO, Response.PROBABLY_NO]
    
    def _is_strong_negative(self, response: Response) -> bool:
        """Check if response is strong negative (SN)"""
        return response == Response.STRONG_NO
    
    def _is_weak_negative_or_ni(self, response: Response) -> bool:
        """Check if response is weak negative or no information (WN/NI)"""
        return response in [Response.WEAK_NO, Response.NO_INFORMATION]
    
    def _is_strong_yes(self, response: Response) -> bool:
        """Check if response is strong yes (SY)"""
        return response == Response.STRONG_YES
    
    def _is_weak_yes_or_ni(self, response: Response) -> bool:
        """Check if response is weak yes or no information (WY/NI)"""
        return response in [Response.WEAK_YES, Response.NO_INFORMATION]

    def _assess_bias_severity(self, bias_level: BiasLevel, context: str = "") -> RiskLevel:
        """
        Convert bias severity to risk level based on context
        This would typically involve domain expert judgment
        """
        # Simplified mapping - in practice this would involve more complex assessment
        if bias_level == BiasLevel.LOW:
            return RiskLevel.LOW_RISK
        elif bias_level == BiasLevel.SOME:
            return RiskLevel.SOME_CONCERNS
        else:  # HIGH
            return RiskLevel.HIGH_RISK

    def _handle_mismeasurement_path(self, responses: Dict[str, Response], pathway: list) -> Dict[str, Any]:
        """
        Handle the mismeasurement/misclassification assessment path
        """
        pathway.append("Entering mismeasurement/misclassification assessment")
        
        # Check Q2.4 Important non-differential error?
        q2_4 = responses.get('q2_4_non_differential_error')
        if q2_4:
            pathway.append(f"Q2.4 Important non-differential error? -> {q2_4.value}")
            
            if self._is_negative_response(q2_4):
                # Go to Q2.3
                q2_3 = responses.get('q2_3_measurement_differential')
                if q2_3:
                    pathway.append(f"Q2.3 Measurement error differential? -> {q2_3.value}")
                    
                    if self._is_weak_yes_or_ni(q2_3):
                        # Back to Q2.4 (circular reference in flowchart)
                        pathway.append("Circular reference to Q2.4 detected")
                        return {
                            'risk_level': RiskLevel.SOME_CONCERNS,
                            'pathway': pathway,
                            'bias_source': 'measurement_uncertainty'
                        }
                    
                    if self._is_strong_yes(q2_3):
                        pathway.append("Strong differential error -> HIGH RISK")
                        return {
                            'risk_level': RiskLevel.HIGH_RISK,
                            'pathway': pathway,
                            'bias_source': 'differential_measurement_error'
                        }
            
            elif self._is_strong_yes(q2_4):
                pathway.append("Important non-differential error -> HIGH RISK")
                return {
                    'risk_level': RiskLevel.HIGH_RISK,
                    'pathway': pathway,
                    'bias_source': 'non_differential_error'
                }
            
            elif self._is_negative_response(q2_4):
                return {
                    'risk_level': RiskLevel.SOME_CONCERNS,
                    'pathway': pathway,
                    'bias_source': 'minor_measurement_issues'
                }
            
            elif self._is_weak_yes_or_ni(q2_4):
                # Could lead to LOW RISK or SOME CONCERNS based on further assessment
                return {
                    'risk_level': RiskLevel.SOME_CONCERNS,
                    'pathway': pathway,
                    'bias_source': 'uncertain_measurement_impact'
                }
        
        # Default if Q2.4 not provided
        return {
            'risk_level': RiskLevel.SOME_CONCERNS,
            'pathway': pathway + ["Default assessment due to incomplete responses"],
            'bias_source': 'incomplete_assessment'
        }

    def _handle_bias_estimation(self, responses: Dict[str, Response], pathway: list, 
                              bias_context: str = "") -> Dict[str, Any]:
        """
        Handle the bias estimation and severity assessment
        """
        pathway.append(f"Bias estimation required: {bias_context}")
        
        # In a real implementation, this would involve more sophisticated bias assessment
        # For now, we'll use a simplified approach based on the responses
        
        q2_2 = responses.get('q2_2_error_single_timepoint')
        if q2_2:
            if self._is_negative_response(q2_2):
                # No error at single time point suggests lower bias
                bias_level = BiasLevel.LOW
            elif self._is_weak_yes_or_ni(q2_2):
                bias_level = BiasLevel.SOME
            elif self._is_strong_yes(q2_2):
                bias_level = BiasLevel.HIGH
            else:
                bias_level = BiasLevel.SOME
        else:
            bias_level = BiasLevel.SOME
        
        pathway.append(f"Assessed bias level: {bias_level.value}")
        
        # Convert bias level to risk level
        risk_level = self._assess_bias_severity(bias_level, bias_context)
        
        # Check if very high risk conditions are met
        # This would be based on additional criteria in practice
        if (bias_level == BiasLevel.HIGH and 
            any(self._is_strong_yes(resp) for resp in responses.values() if resp)):
            risk_level = RiskLevel.VERY_HIGH_RISK
            pathway.append("Elevated to VERY HIGH RISK due to severe bias indicators")
        
        return {
            'risk_level': risk_level,
            'pathway': pathway,
            'bias_level': bias_level,
            'bias_source': bias_context
        }

    def assess_exposure_measurement_bias(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Assess risk of bias due to measurement of exposure
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with risk assessment and pathway taken
        """
        pathway = []
        
        # Start with Q2.1 Exposure measures well characterise exposure of interest?
        q2_1 = responses.get('q2_1_exposure_characterise')
        if not q2_1:
            return {
                'risk_level': RiskLevel.SOME_CONCERNS,
                'pathway': ["Missing Q2.1 response"],
                'bias_source': 'incomplete_data'
            }
        
        pathway.append(f"Q2.1 Exposure measures well characterise exposure of interest? -> {q2_1.value}")
        
        # Handle strong negative response - leads to mismeasurement path
        if self._is_strong_negative(q2_1):
            pathway.append("SN path -> Mismeasurement/misclassification assessment")
            return self._handle_mismeasurement_path(responses, pathway)
        
        # Handle positive responses and weak negative/NI - go to Q2.2
        if (self._is_positive_response(q2_1) or 
            self._is_weak_negative_or_ni(q2_1)):
            
            q2_2 = responses.get('q2_2_error_single_timepoint')
            if not q2_2:
                return {
                    'risk_level': RiskLevel.SOME_CONCERNS,
                    'pathway': pathway + ["Missing Q2.2 response"],
                    'bias_source': 'incomplete_data'
                }
            
            pathway.append(f"Q2.2 Error in measurement at a single time point? -> {q2_2.value}")
            
            # All responses from Q2.2 lead to bias estimation
            if self._is_negative_response(q2_2):
                return self._handle_bias_estimation(responses, pathway, "minimal_single_timepoint_error")
            elif self._is_weak_yes_or_ni(q2_2):
                return self._handle_bias_estimation(responses, pathway, "some_single_timepoint_error")
            elif self._is_strong_yes(q2_2):
                return self._handle_bias_estimation(responses, pathway, "significant_single_timepoint_error")
            else:
                return self._handle_bias_estimation(responses, pathway, "unspecified_single_timepoint_error")
        
        # Default fallback
        return {
            'risk_level': RiskLevel.SOME_CONCERNS,
            'pathway': pathway + ["Fallback due to unhandled response pattern"],
            'bias_source': 'unhandled_case'
        }

    def get_questions(self) -> Dict[str, str]:
        """Return the algorithm questions"""
        return self.questions.copy()

# Example usage and testing
if __name__ == "__main__":
    robins_e_d2 = ROBINSEDomain2()
    
    # Example 1: Low risk scenario - well characterized exposure, no measurement error
    responses_low = {
        'q2_1_exposure_characterise': Response.YES,
        'q2_2_error_single_timepoint': Response.NO
    }
    
    result_low = robins_e_d2.assess_exposure_measurement_bias(responses_low)
    print("=== Low Risk Example ===")
    print(f"Risk Level: {result_low['risk_level'].value}")
    print(f"Bias Source: {result_low['bias_source']}")
    print(f"Pathway: {' -> '.join(result_low['pathway'])}")
    print()
    
    # Example 2: High risk scenario - poorly characterized exposure
    responses_high = {
        'q2_1_exposure_characterise': Response.STRONG_NO,
        'q2_4_non_differential_error': Response.STRONG_YES
    }
    
    result_high = robins_e_d2.assess_exposure_measurement_bias(responses_high)
    print("=== High Risk Example ===")
    print(f"Risk Level: {result_high['risk_level'].value}")
    print(f"Bias Source: {result_high['bias_source']}")
    print(f"Pathway: {' -> '.join(result_high['pathway'])}")
    print()
    
    # Example 3: Some concerns scenario - measurement uncertainty
    responses_concerns = {
        'q2_1_exposure_characterise': Response.WEAK_NO,
        'q2_2_error_single_timepoint': Response.WEAK_YES
    }
    
    result_concerns = robins_e_d2.assess_exposure_measurement_bias(responses_concerns)
    print("=== Some Concerns Example ===")
    print(f"Risk Level: {result_concerns['risk_level'].value}")
    print(f"Bias Source: {result_concerns['bias_source']}")
    print(f"Pathway: {' -> '.join(result_concerns['pathway'])}")
    print()
    
    # Example 4: Differential measurement error scenario
    responses_differential = {
        'q2_1_exposure_characterise': Response.STRONG_NO,
        'q2_4_non_differential_error': Response.NO,
        'q2_3_measurement_differential': Response.STRONG_YES
    }
    
    result_differential = robins_e_d2.assess_exposure_measurement_bias(responses_differential)
    print("=== Differential Measurement Error Example ===")
    print(f"Risk Level: {result_differential['risk_level'].value}")
    print(f"Bias Source: {result_differential['bias_source']}")
    print(f"Pathway: {' -> '.join(result_differential['pathway'])}")
    print()
    
    # Print available questions for reference
    print("=== Available Questions ===")
    for key, question in robins_e_d2.get_questions().items():
        print(f"{key}: {question}")
