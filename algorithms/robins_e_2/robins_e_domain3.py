"""
ROBINS-E Tool Domain 3: Risk of Bias due to Selection and Timing Issues
Implementation covering both Pathway A (timing) and Pathway B (selection)
"""

from enum import Enum
from typing import Dict, Any, Tuple

class Response(Enum):
    """Possible responses to algorithm questions"""
    YES = "Y"
    PROBABLY_YES = "PY"
    NO = "N"
    PROBABLY_NO = "PN"
    NO_INFORMATION = "NI"
    STRONG_NO = "SN"
    WEAK_NO = "WN"

class PathwayRisk(Enum):
    """Risk levels for individual pathways"""
    LOW_RISK = "Low risk of bias"
    SOME_CONCERNS = "Some concerns"
    HIGH_RISK = "High risk of bias"

class RiskLevel(Enum):
    """Final risk of bias levels"""
    LOW_RISK = "Low risk of bias"
    SOME_CONCERNS = "Some concerns"
    HIGH_RISK = "High risk of bias"
    VERY_HIGH_RISK = "Very high risk of bias"

class ROBINSEDomain3:
    """ROBINS-E Domain 3 Algorithm Implementation"""
    
    def __init__(self):
        self.questions = {
            # Pathway A - Timing
            'q3_1_timing_coincide': "3.1 Starts of exposure and follow-up coincide?",
            'q3_2_effect_constant': "3.2 Effect constant over time?",
            
            # Pathway B - Selection
            'q3_3_selection_after_start': "3.3 Selection based on characteristics after start?",
            'q3_4_selection_by_exposure': "3.4 Selection variables influenced by exposure?",
            'q3_5_selection_by_outcome': "3.5 Selection variables influenced by outcome?",
            
            # Final assessment
            'q3_6_analysis_corrected': "3.6 Analysis corrected for selection biases?",
            'q3_7_sensitivity_analysis': "3.7 Sensitivity analyses demonstrate minimal impact?"
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
    
    def _is_negative_or_ni(self, response: Response) -> bool:
        """Check if response is negative or no information (N/PN/NI)"""
        return response in [Response.NO, Response.PROBABLY_NO, Response.NO_INFORMATION]

    def _assess_pathway_a(self, responses: Dict[str, Response]) -> Tuple[PathwayRisk, list]:
        """
        Assess Pathway A - Timing issues
        
        Returns:
            Tuple of (PathwayRisk, pathway_log)
        """
        pathway = []
        
        q3_1 = responses.get('q3_1_timing_coincide')
        if not q3_1:
            return PathwayRisk.SOME_CONCERNS, ["Missing Q3.1 response"]
        
        pathway.append(f"Q3.1 Starts of exposure and follow-up coincide? -> {q3_1.value}")
        
        # Both Y/PY and N/PN paths go to Q3.2
        q3_2 = responses.get('q3_2_effect_constant')
        if not q3_2:
            return PathwayRisk.SOME_CONCERNS, pathway + ["Missing Q3.2 response"]
        
        pathway.append(f"Q3.2 Effect constant over time? -> {q3_2.value}")
        
        # Determine outcome based on Q3.1 and Q3.2 responses
        if self._is_positive_response(q3_1):
            # Y/PY path from Q3.1
            if self._is_positive_response(q3_2):
                return PathwayRisk.LOW_RISK, pathway
            elif self._is_positive_or_ni(q3_2):
                return PathwayRisk.SOME_CONCERNS, pathway
            elif self._is_negative_response(q3_2):
                return PathwayRisk.HIGH_RISK, pathway
        else:
            # N/PN path from Q3.1
            if self._is_positive_response(q3_2):
                return PathwayRisk.LOW_RISK, pathway
            elif self._is_positive_or_ni(q3_2):
                return PathwayRisk.SOME_CONCERNS, pathway
            elif self._is_negative_response(q3_2):
                return PathwayRisk.HIGH_RISK, pathway
        
        # Default fallback
        return PathwayRisk.SOME_CONCERNS, pathway

    def _assess_pathway_b(self, responses: Dict[str, Response]) -> Tuple[PathwayRisk, list]:
        """
        Assess Pathway B - Selection bias
        
        Returns:
            Tuple of (PathwayRisk, pathway_log)
        """
        pathway = []
        
        q3_3 = responses.get('q3_3_selection_after_start')
        if not q3_3:
            return PathwayRisk.SOME_CONCERNS, ["Missing Q3.3 response"]
        
        pathway.append(f"Q3.3 Selection based on characteristics after start? -> {q3_3.value}")
        
        if self._is_positive_response(q3_3):
            # Y/PY -> HIGH RISK
            return PathwayRisk.HIGH_RISK, pathway
        
        elif q3_3 == Response.NO_INFORMATION:
            # NI -> SOME CONCERNS
            return PathwayRisk.SOME_CONCERNS, pathway
        
        elif self._is_negative_response(q3_3):
            # N/PN -> Q3.4
            q3_4 = responses.get('q3_4_selection_by_exposure')
            if not q3_4:
                return PathwayRisk.SOME_CONCERNS, pathway + ["Missing Q3.4 response"]
            
            pathway.append(f"Q3.4 Selection variables influenced by exposure? -> {q3_4.value}")
            
            if q3_4 == Response.NO_INFORMATION:
                # NI -> SOME CONCERNS
                return PathwayRisk.SOME_CONCERNS, pathway
            
            elif self._is_negative_response(q3_4):
                # N/PN -> Q3.5
                q3_5 = responses.get('q3_5_selection_by_outcome')
                if not q3_5:
                    return PathwayRisk.SOME_CONCERNS, pathway + ["Missing Q3.5 response"]
                
                pathway.append(f"Q3.5 Selection variables influenced by outcome? -> {q3_5.value}")
                
                if self._is_negative_response(q3_5):
                    return PathwayRisk.LOW_RISK, pathway
                elif self._is_positive_response(q3_5):
                    return PathwayRisk.HIGH_RISK, pathway
                
            elif self._is_positive_response(q3_4):
                # Y/PY -> Q3.5
                q3_5 = responses.get('q3_5_selection_by_outcome')
                if not q3_5:
                    return PathwayRisk.SOME_CONCERNS, pathway + ["Missing Q3.5 response"]
                
                pathway.append(f"Q3.5 Selection variables influenced by outcome? -> {q3_5.value}")
                
                if self._is_negative_or_ni(q3_5):
                    return PathwayRisk.SOME_CONCERNS, pathway
                elif self._is_positive_response(q3_5):
                    return PathwayRisk.HIGH_RISK, pathway
        
        # Default fallback
        return PathwayRisk.SOME_CONCERNS, pathway

    def _combine_pathway_risks(self, pathway_a_risk: PathwayRisk, pathway_b_risk: PathwayRisk,
                              responses: Dict[str, Response], pathway: list) -> Dict[str, Any]:
        """
        Combine risks from Pathway A and B according to "Across A, B" rules
        """
        pathway.append(f"Pathway A risk: {pathway_a_risk.value}")
        pathway.append(f"Pathway B risk: {pathway_b_risk.value}")
        
        # Both LOW -> LOW RISK
        if (pathway_a_risk == PathwayRisk.LOW_RISK and 
            pathway_b_risk == PathwayRisk.LOW_RISK):
            return {
                'risk_level': RiskLevel.LOW_RISK,
                'pathway': pathway,
                'pathway_a_risk': pathway_a_risk,
                'pathway_b_risk': pathway_b_risk,
                'combination_rule': 'both_low'
            }
        
        # One or both SOME but neither HIGH -> SOME CONCERNS
        if ((pathway_a_risk == PathwayRisk.SOME_CONCERNS or 
             pathway_b_risk == PathwayRisk.SOME_CONCERNS) and
            pathway_a_risk != PathwayRisk.HIGH_RISK and 
            pathway_b_risk != PathwayRisk.HIGH_RISK):
            return {
                'risk_level': RiskLevel.SOME_CONCERNS,
                'pathway': pathway,
                'pathway_a_risk': pathway_a_risk,
                'pathway_b_risk': pathway_b_risk,
                'combination_rule': 'some_concerns_no_high'
            }
        
        # At least one HIGH -> Additional assessment needed
        if (pathway_a_risk == PathwayRisk.HIGH_RISK or 
            pathway_b_risk == PathwayRisk.HIGH_RISK):
            pathway.append("At least one HIGH risk - checking corrections")
            
            # Q3.6 Analysis corrected for selection biases?
            q3_6 = responses.get('q3_6_analysis_corrected')
            if q3_6 and self._is_positive_response(q3_6):
                pathway.append(f"Q3.6 Analysis corrected for selection biases? -> {q3_6.value} -> SOME CONCERNS")
                return {
                    'risk_level': RiskLevel.SOME_CONCERNS,
                    'pathway': pathway,
                    'pathway_a_risk': pathway_a_risk,
                    'pathway_b_risk': pathway_b_risk,
                    'combination_rule': 'corrected_analysis'
                }
            
            # If not corrected or N/PN/NI, go to Q3.7
            if q3_6:
                pathway.append(f"Q3.6 Analysis corrected for selection biases? -> {q3_6.value}")
            
            q3_7 = responses.get('q3_7_sensitivity_analysis')
            if not q3_7:
                return {
                    'risk_level': RiskLevel.HIGH_RISK,
                    'pathway': pathway + ["Missing Q3.7 response -> HIGH RISK"],
                    'pathway_a_risk': pathway_a_risk,
                    'pathway_b_risk': pathway_b_risk,
                    'combination_rule': 'high_risk_default'
                }
            
            pathway.append(f"Q3.7 Sensitivity analyses demonstrate minimal impact? -> {q3_7.value}")
            
            if self._is_positive_response(q3_7):
                return {
                    'risk_level': RiskLevel.SOME_CONCERNS,
                    'pathway': pathway,
                    'pathway_a_risk': pathway_a_risk,
                    'pathway_b_risk': pathway_b_risk,
                    'combination_rule': 'sensitivity_analysis_positive'
                }
            elif q3_7 == Response.WEAK_NO:
                return {
                    'risk_level': RiskLevel.HIGH_RISK,
                    'pathway': pathway,
                    'pathway_a_risk': pathway_a_risk,
                    'pathway_b_risk': pathway_b_risk,
                    'combination_rule': 'sensitivity_analysis_weak_no'
                }
            elif q3_7 == Response.STRONG_NO:
                return {
                    'risk_level': RiskLevel.VERY_HIGH_RISK,
                    'pathway': pathway,
                    'pathway_a_risk': pathway_a_risk,
                    'pathway_b_risk': pathway_b_risk,
                    'combination_rule': 'sensitivity_analysis_strong_no'
                }
            else:
                return {
                    'risk_level': RiskLevel.HIGH_RISK,
                    'pathway': pathway,
                    'pathway_a_risk': pathway_a_risk,
                    'pathway_b_risk': pathway_b_risk,
                    'combination_rule': 'sensitivity_analysis_other'
                }
        
        # Default fallback
        return {
            'risk_level': RiskLevel.SOME_CONCERNS,
            'pathway': pathway + ["Default fallback"],
            'pathway_a_risk': pathway_a_risk,
            'pathway_b_risk': pathway_b_risk,
            'combination_rule': 'fallback'
        }

    def assess_selection_timing_bias(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Assess risk of bias due to selection and timing issues
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with risk assessment and pathway taken
        """
        pathway = []
        
        # Assess Pathway A (timing)
        pathway_a_risk, pathway_a_log = self._assess_pathway_a(responses)
        pathway.extend([f"PATHWAY A: {log}" for log in pathway_a_log])
        
        # Assess Pathway B (selection)
        pathway_b_risk, pathway_b_log = self._assess_pathway_b(responses)
        pathway.extend([f"PATHWAY B: {log}" for log in pathway_b_log])
        
        # Combine pathway results
        result = self._combine_pathway_risks(pathway_a_risk, pathway_b_risk, responses, pathway)
        
        return result

    def get_questions(self) -> Dict[str, str]:
        """Return the algorithm questions"""
        return self.questions.copy()

# Example usage and testing
if __name__ == "__main__":
    robins_e_d3 = ROBINSEDomain3()
    
    # Example 1: Low risk scenario - both pathways low risk
    responses_low = {
        'q3_1_timing_coincide': Response.YES,
        'q3_2_effect_constant': Response.YES,
        'q3_3_selection_after_start': Response.NO,
        'q3_4_selection_by_exposure': Response.NO,
        'q3_5_selection_by_outcome': Response.NO
    }
    
    result_low = robins_e_d3.assess_selection_timing_bias(responses_low)
    print("=== Low Risk Example ===")
    print(f"Risk Level: {result_low['risk_level'].value}")
    print(f"Pathway A Risk: {result_low['pathway_a_risk'].value}")
    print(f"Pathway B Risk: {result_low['pathway_b_risk'].value}")
    print(f"Combination Rule: {result_low['combination_rule']}")
    print()
    
    # Example 2: High risk with correction - some concerns
    responses_corrected = {
        'q3_1_timing_coincide': Response.NO,
        'q3_2_effect_constant': Response.NO,  # HIGH risk from pathway A
        'q3_3_selection_after_start': Response.NO,
        'q3_4_selection_by_exposure': Response.NO,
        'q3_5_selection_by_outcome': Response.NO,  # LOW risk from pathway B
        'q3_6_analysis_corrected': Response.YES  # Corrected analysis
    }
    
    result_corrected = robins_e_d3.assess_selection_timing_bias(responses_corrected)
    print("=== High Risk with Correction Example ===")
    print(f"Risk Level: {result_corrected['risk_level'].value}")
    print(f"Pathway A Risk: {result_corrected['pathway_a_risk'].value}")
    print(f"Pathway B Risk: {result_corrected['pathway_b_risk'].value}")
    print(f"Combination Rule: {result_corrected['combination_rule']}")
    print()
    
    # Example 3: Very high risk scenario
    responses_very_high = {
        'q3_1_timing_coincide': Response.YES,
        'q3_2_effect_constant': Response.YES,  # LOW risk from pathway A
        'q3_3_selection_after_start': Response.YES,  # HIGH risk from pathway B
        'q3_6_analysis_corrected': Response.NO,
        'q3_7_sensitivity_analysis': Response.STRONG_NO
    }
    
    result_very_high = robins_e_d3.assess_selection_timing_bias(responses_very_high)
    print("=== Very High Risk Example ===")
    print(f"Risk Level: {result_very_high['risk_level'].value}")
    print(f"Pathway A Risk: {result_very_high['pathway_a_risk'].value}")
    print(f"Pathway B Risk: {result_very_high['pathway_b_risk'].value}")
    print(f"Combination Rule: {result_very_high['combination_rule']}")
    print()
    
    # Example 4: Some concerns scenario
    responses_concerns = {
        'q3_1_timing_coincide': Response.YES,
        'q3_2_effect_constant': Response.NO_INFORMATION,  # SOME concerns from pathway A
        'q3_3_selection_after_start': Response.NO,
        'q3_4_selection_by_exposure': Response.NO,
        'q3_5_selection_by_outcome': Response.NO  # LOW risk from pathway B
    }
    
    result_concerns = robins_e_d3.assess_selection_timing_bias(responses_concerns)
    print("=== Some Concerns Example ===")
    print(f"Risk Level: {result_concerns['risk_level'].value}")
    print(f"Pathway A Risk: {result_concerns['pathway_a_risk'].value}")
    print(f"Pathway B Risk: {result_concerns['pathway_b_risk'].value}")
    print(f"Combination Rule: {result_concerns['combination_rule']}")
    print()
    
    # Print available questions for reference
    print("=== Available Questions ===")
    for key, question in robins_e_d3.get_questions().items():
        print(f"{key}: {question}")
