"""
ROBINS-E Tool Domain 1: Risk of Bias due to Confounding
Implementation of both Variant A and Variant B algorithms
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
    STRONG_NO = "SN"
    WEAK_NO = "WN"
    VERY_PROBABLY_YES = "VPY"

class RiskLevel(Enum):
    """Risk of bias levels"""
    LOW_RISK = "Low risk of bias (except for concerns about uncontrolled confounding)"
    SOME_CONCERNS = "Some concerns"
    HIGH_RISK = "High risk of bias"
    VERY_HIGH_RISK = "Very high risk of bias"

class ROBINSEDomain1:
    """ROBINS-E Domain 1 Algorithm Implementation"""
    
    def __init__(self):
        self.questions = {
            'q1_1_appropriate_method': "1.1 Appropriate analysis method?",
            'q1_1_controlled_important': "1.1 Controlled for all the important confounding factors?",
            'q1_2_controlled_important': "1.2 Controlled for all the important confounding factors?",
            'q1_2_factors_measured': "1.2 Confounding factors measured validly and reliably?",
            'q1_3_factors_measured': "1.3 Confounding factors measured validly and reliably?", 
            'q1_3_post_exposure': "1.3 Control for any post-exposure variables?",
            'q1_4_post_exposure_vars': "1.4 Controlled for variables measured after start of exposure?",
            'q1_4_negative_controls': "1.4 Negative controls etc suggest serious uncontrolled confounding?",
            'q1_5_negative_controls': "1.5 Negative controls etc suggest serious uncontrolled confounding?"
        }
    
    def _is_positive_response(self, response: Response) -> bool:
        """Check if response is positive (Y/PY)"""
        return response in [Response.YES, Response.PROBABLY_YES]
    
    def _is_negative_response(self, response: Response) -> bool:
        """Check if response is negative (N/PN)"""
        return response in [Response.NO, Response.PROBABLY_NO]
    
    def _is_strong_negative(self, response: Response) -> bool:
        """Check if response is strong negative (SN/NI)"""
        return response in [Response.STRONG_NO, Response.NO_INFORMATION]
    
    def _is_weak_negative(self, response: Response) -> bool:
        """Check if response is weak negative (WN)"""
        return response == Response.WEAK_NO
    
    def _is_very_probably_yes_or_weak_no(self, response: Response) -> bool:
        """Check if response is VPY/WN"""
        return response in [Response.VERY_PROBABLY_YES, Response.WEAK_NO]

    def variant_b_algorithm(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        ROBINS-E Domain 1 Variant B Algorithm
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with risk assessment and pathway taken
        """
        pathway = []
        
        # Start with Q1.1 Appropriate analysis method?
        q1_1 = responses.get('q1_1_appropriate_method')
        pathway.append(f"Q1.1 Appropriate analysis method? -> {q1_1.value}")
        
        if q1_1 in [Response.NO, Response.PROBABLY_NO, Response.NO_INFORMATION]:
            pathway.append("Direct path to HIGH RISK")
            return {
                'risk_level': RiskLevel.HIGH_RISK,
                'pathway': pathway,
                'variant': 'B'
            }
        
        # If Y/PY, go to Q1.2 Controlled for all important confounding factors?
        if self._is_positive_response(q1_1):
            q1_2 = responses.get('q1_2_controlled_important')
            pathway.append(f"Q1.2 Controlled for all important confounding factors? -> {q1_2.value}")
            
            if self._is_strong_negative(q1_2):
                pathway.append("SN/NI path to HIGH RISK")
                return {
                    'risk_level': RiskLevel.HIGH_RISK,
                    'pathway': pathway,
                    'variant': 'B'
                }
            
            if self._is_weak_negative(q1_2):
                # WN path to Q1.4
                q1_4_vars = responses.get('q1_4_post_exposure_vars')
                pathway.append(f"Q1.4 Controlled for variables measured after start of exposure? -> {q1_4_vars.value}")
                
                if self._is_positive_response(q1_4_vars):
                    pathway.append("Y/PY path to VERY HIGH RISK")
                    return {
                        'risk_level': RiskLevel.VERY_HIGH_RISK,
                        'pathway': pathway,
                        'variant': 'B'
                    }
                else:
                    # Continue to Q1.5
                    q1_5 = responses.get('q1_5_negative_controls')
                    pathway.append(f"Q1.5 Negative controls suggest serious uncontrolled confounding? -> {q1_5.value}")
                    
                    if self._is_positive_response(q1_5):
                        return {
                            'risk_level': RiskLevel.SOME_CONCERNS,
                            'pathway': pathway,
                            'variant': 'B'
                        }
                    else:
                        return {
                            'risk_level': RiskLevel.LOW_RISK,
                            'pathway': pathway,
                            'variant': 'B'
                        }
            
            # If Y/PY, go to Q1.3
            if self._is_positive_response(q1_2):
                q1_3 = responses.get('q1_3_factors_measured')
                pathway.append(f"Q1.3 Confounding factors measured validly and reliably? -> {q1_3.value}")
                
                if self._is_strong_negative(q1_3):
                    pathway.append("SN/NI path to HIGH RISK")
                    return {
                        'risk_level': RiskLevel.HIGH_RISK,
                        'pathway': pathway,
                        'variant': 'B'
                    }
                
                # Continue to Q1.5
                q1_5 = responses.get('q1_5_negative_controls')
                pathway.append(f"Q1.5 Negative controls suggest serious uncontrolled confounding? -> {q1_5.value}")
                
                if self._is_positive_response(q1_5):
                    return {
                        'risk_level': RiskLevel.SOME_CONCERNS,
                        'pathway': pathway,
                        'variant': 'B'
                    }
                else:
                    return {
                        'risk_level': RiskLevel.LOW_RISK,
                        'pathway': pathway,
                        'variant': 'B'
                    }
        
        # Default fallback
        return {
            'risk_level': RiskLevel.HIGH_RISK,
            'pathway': pathway + ["Fallback to HIGH RISK"],
            'variant': 'B'
        }

    def variant_a_algorithm(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        ROBINS-E Domain 1 Variant A Algorithm
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with risk assessment and pathway taken
        """
        pathway = []
        
        # Start with Q1.1 Controlled for all important confounding factors?
        q1_1 = responses.get('q1_1_controlled_important')
        pathway.append(f"Q1.1 Controlled for all important confounding factors? -> {q1_1.value}")
        
        if self._is_strong_negative(q1_1):
            pathway.append("SN/NI path to HIGH RISK")
            return {
                'risk_level': RiskLevel.HIGH_RISK,
                'pathway': pathway,
                'variant': 'A'
            }
        
        # Handle Y/PY and WN paths
        if self._is_positive_response(q1_1) or self._is_weak_negative(q1_1):
            q1_3_post = responses.get('q1_3_post_exposure')
            pathway.append(f"Q1.3 Control for any post-exposure variables? -> {q1_3_post.value}")
            
            if self._is_positive_response(q1_3_post):
                # Direct to Q1.4 negative controls
                q1_4_neg = responses.get('q1_4_negative_controls')
                pathway.append(f"Q1.4 Negative controls suggest serious uncontrolled confounding? -> {q1_4_neg.value}")
                
                if self._is_positive_response(q1_4_neg):
                    return {
                        'risk_level': RiskLevel.SOME_CONCERNS,
                        'pathway': pathway,
                        'variant': 'A'
                    }
                else:
                    return {
                        'risk_level': RiskLevel.LOW_RISK,
                        'pathway': pathway,
                        'variant': 'A'
                    }
            
            # If N/PN, go to Q1.2
            if self._is_negative_response(q1_3_post):
                q1_2 = responses.get('q1_2_factors_measured')
                pathway.append(f"Q1.2 Confounding factors measured validly and reliably? -> {q1_2.value}")
                
                if self._is_strong_negative(q1_2):
                    pathway.append("SN/NI path to HIGH RISK")
                    return {
                        'risk_level': RiskLevel.HIGH_RISK,
                        'pathway': pathway,
                        'variant': 'A'
                    }
                
                if self._is_positive_response(q1_2):
                    # Check if this leads to VERY HIGH RISK path
                    pathway.append("Y/PY path to VERY HIGH RISK")
                    return {
                        'risk_level': RiskLevel.VERY_HIGH_RISK,
                        'pathway': pathway,
                        'variant': 'A'
                    }
                
                # Continue to Q1.4 negative controls
                q1_4_neg = responses.get('q1_4_negative_controls')
                pathway.append(f"Q1.4 Negative controls suggest serious uncontrolled confounding? -> {q1_4_neg.value}")
                
                if self._is_positive_response(q1_4_neg):
                    return {
                        'risk_level': RiskLevel.SOME_CONCERNS,
                        'pathway': pathway,
                        'variant': 'A'
                    }
                else:
                    return {
                        'risk_level': RiskLevel.LOW_RISK,
                        'pathway': pathway,
                        'variant': 'A'
                    }
        
        # Default fallback
        return {
            'risk_level': RiskLevel.HIGH_RISK,
            'pathway': pathway + ["Fallback to HIGH RISK"],
            'variant': 'A'
        }

    def assess_bias_risk(self, responses: Dict[str, Response], variant: str = 'B') -> Dict[str, Any]:
        """
        Assess risk of bias using specified variant
        
        Args:
            responses: Dictionary of responses to algorithm questions
            variant: 'A' or 'B' to specify which algorithm variant to use
            
        Returns:
            Dictionary with risk assessment results
        """
        if variant.upper() == 'A':
            return self.variant_a_algorithm(responses)
        elif variant.upper() == 'B':
            return self.variant_b_algorithm(responses)
        else:
            raise ValueError("Variant must be 'A' or 'B'")

# Example usage and testing
if __name__ == "__main__":
    robins_e = ROBINSEDomain1()
    
    # Example 1: Variant B - Low risk scenario
    responses_b_low = {
        'q1_1_appropriate_method': Response.YES,
        'q1_2_controlled_important': Response.YES,
        'q1_3_factors_measured': Response.YES,
        'q1_5_negative_controls': Response.NO
    }
    
    result_b_low = robins_e.assess_bias_risk(responses_b_low, variant='B')
    print("=== Variant B - Low Risk Example ===")
    print(f"Risk Level: {result_b_low['risk_level'].value}")
    print(f"Pathway: {' -> '.join(result_b_low['pathway'])}")
    print()
    
    # Example 2: Variant B - High risk scenario
    responses_b_high = {
        'q1_1_appropriate_method': Response.NO
    }
    
    result_b_high = robins_e.assess_bias_risk(responses_b_high, variant='B')
    print("=== Variant B - High Risk Example ===")
    print(f"Risk Level: {result_b_high['risk_level'].value}")
    print(f"Pathway: {' -> '.join(result_b_high['pathway'])}")
    print()
    
    # Example 3: Variant A - Some concerns scenario
    responses_a_concerns = {
        'q1_1_controlled_important': Response.YES,
        'q1_3_post_exposure': Response.YES,
        'q1_4_negative_controls': Response.YES
    }
    
    result_a_concerns = robins_e.assess_bias_risk(responses_a_concerns, variant='A')
    print("=== Variant A - Some Concerns Example ===")
    print(f"Risk Level: {result_a_concerns['risk_level'].value}")
    print(f"Pathway: {' -> '.join(result_a_concerns['pathway'])}")
    print()
    
    # Print available questions for reference
    print("=== Available Questions ===")
    for key, question in robins_e.questions.items():
        print(f"{key}: {question}")
