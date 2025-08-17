"""
ROBINS-E Tool Domain 5: Risk of Bias due to Missing Data
Implementation of the algorithm for assessing bias from missing data and analysis methods
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
    STRONG_YES = "SY"
    WEAK_YES = "WY"
    STRONG_NO = "SN"
    WEAK_NO = "WN"

class RiskLevel(Enum):
    """Risk of bias levels"""
    LOW_RISK = "Low risk of bias"
    SOME_CONCERNS = "Some concerns"
    HIGH_RISK = "High risk of bias"
    VERY_HIGH_RISK = "Very high risk of bias"

class ROBINSEDomain5:
    """ROBINS-E Domain 5 Algorithm Implementation"""
    
    def __init__(self):
        self.questions = {
            'q5_1_to_5_3_complete_data': "5.1-5.3 Complete data for all participants?",
            'q5_4_complete_case_analysis': "5.4 Complete case analysis?",
            'q5_5_exclusion_related_outcome': "5.5 Exclusion from analysis related to true value of outcome?",
            'q5_6_predictors_missingness': "5.6 Predictors of missingness included in model?",
            'q5_7_analysis_imputing': "5.7 Analysis based on imputing missing values?",
            'q5_8_appropriate_imputation': "5.8 Appropriate imputation?",
            'q5_9_appropriate_method': "5.9 Appropriate method?",
            'q5_10_evidence_not_biased': "5.10 Evidence that result is not biased?"
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
    
    def _is_weak_or_ni(self, response: Response) -> bool:
        """Check if response is weak or no information (WY/WN/NI)"""
        return response in [Response.WEAK_YES, Response.WEAK_NO, Response.NO_INFORMATION]
    
    def _is_strong_response(self, response: Response) -> bool:
        """Check if response is strong (SY/SN)"""
        return response in [Response.STRONG_YES, Response.STRONG_NO]

    def _assess_evidence_pathway(self, q5_10_response: Response, pathway_context: str) -> Dict[str, Any]:
        """
        Assess Q5.10 Evidence that result is not biased based on pathway context
        Different pathways to Q5.10 have different outcome mappings
        """
        if not q5_10_response:
            return {
                'risk_level': RiskLevel.HIGH_RISK,
                'rationale': f'missing_evidence_assessment_{pathway_context}'
            }
        
        # The outcome depends on both the response and the pathway context
        if pathway_context in ['predictors_included', 'exclusion_unrelated', 'appropriate_imputation', 'appropriate_method']:
            # These pathways typically have better outcomes for positive evidence
            if self._is_positive_response(q5_10_response):
                return {
                    'risk_level': RiskLevel.SOME_CONCERNS,
                    'rationale': f'evidence_supports_low_bias_{pathway_context}'
                }
            elif self._is_negative_response(q5_10_response):
                return {
                    'risk_level': RiskLevel.HIGH_RISK,
                    'rationale': f'evidence_suggests_bias_{pathway_context}'
                }
        
        elif pathway_context in ['exclusion_related', 'poor_imputation', 'poor_method']:
            # These pathways typically have worse outcomes even with positive evidence
            if self._is_positive_response(q5_10_response):
                return {
                    'risk_level': RiskLevel.SOME_CONCERNS,
                    'rationale': f'evidence_supports_but_concerns_remain_{pathway_context}'
                }
            elif self._is_negative_response(q5_10_response):
                return {
                    'risk_level': RiskLevel.VERY_HIGH_RISK,
                    'rationale': f'evidence_confirms_bias_{pathway_context}'
                }
        
        else:
            # Default moderate assessment for unclear pathways
            if self._is_positive_response(q5_10_response):
                return {
                    'risk_level': RiskLevel.SOME_CONCERNS,
                    'rationale': f'evidence_moderate_{pathway_context}'
                }
            elif self._is_negative_response(q5_10_response):
                return {
                    'risk_level': RiskLevel.HIGH_RISK,
                    'rationale': f'evidence_poor_{pathway_context}'
                }
        
        # Default for unclear responses
        return {
            'risk_level': RiskLevel.SOME_CONCERNS,
            'rationale': f'evidence_unclear_{pathway_context}'
        }

    def assess_missing_data_bias(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Assess risk of bias due to missing data
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with risk assessment and pathway taken
        """
        pathway = []
        
        # Start with Q5.1-5.3 Complete data for all participants?
        q5_1_3 = responses.get('q5_1_to_5_3_complete_data')
        if not q5_1_3:
            return {
                'risk_level': RiskLevel.SOME_CONCERNS,
                'pathway': ["Missing Q5.1-5.3 response"],
                'rationale': 'incomplete_data_assessment'
            }
        
        pathway.append(f"Q5.1-5.3 Complete data for all participants? -> {q5_1_3.value}")
        
        # Check for complete data (All Y/PY)
        if q5_1_3 in [Response.YES, Response.PROBABLY_YES]:
            # This assumes "All Y/PY" means the overall assessment is positive
            pathway.append("All Y/PY path -> LOW RISK OF BIAS")
            return {
                'risk_level': RiskLevel.LOW_RISK,
                'pathway': pathway,
                'rationale': 'complete_data_all_participants'
            }
        
        # Any N/PN/NI path - proceed to Q5.4
        pathway.append("Any N/PN/NI path -> Proceeding to Q5.4")
        
        q5_4 = responses.get('q5_4_complete_case_analysis')
        if not q5_4:
            return {
                'risk_level': RiskLevel.HIGH_RISK,
                'pathway': pathway + ["Missing Q5.4 response"],
                'rationale': 'incomplete_analysis_method_assessment'
            }
        
        pathway.append(f"Q5.4 Complete case analysis? -> {q5_4.value}")
        
        # Complete case analysis path
        if self._is_positive_or_ni(q5_4):
            # Y/PY/NI -> Q5.5
            q5_5 = responses.get('q5_5_exclusion_related_outcome')
            if not q5_5:
                return {
                    'risk_level': RiskLevel.HIGH_RISK,
                    'pathway': pathway + ["Missing Q5.5 response"],
                    'rationale': 'incomplete_exclusion_assessment'
                }
            
            pathway.append(f"Q5.5 Exclusion from analysis related to true value of outcome? -> {q5_5.value}")
            
            if self._is_negative_response(q5_5):
                # N/PN -> Q5.6
                q5_6 = responses.get('q5_6_predictors_missingness')
                if not q5_6:
                    return {
                        'risk_level': RiskLevel.HIGH_RISK,
                        'pathway': pathway + ["Missing Q5.6 response"],
                        'rationale': 'incomplete_predictors_assessment'
                    }
                
                pathway.append(f"Q5.6 Predictors of missingness included in model? -> {q5_6.value}")
                
                if q5_6 == Response.STRONG_YES:
                    pathway.append("SY path -> SOME CONCERNS")
                    return {
                        'risk_level': RiskLevel.SOME_CONCERNS,
                        'pathway': pathway,
                        'rationale': 'predictors_included_strong'
                    }
                else:
                    # WY/NI or N/PN -> Q5.10
                    q5_10 = responses.get('q5_10_evidence_not_biased')
                    pathway.append(f"Q5.6 {q5_6.value} -> Proceeding to Q5.10")
                    if q5_10:
                        pathway.append(f"Q5.10 Evidence that result is not biased? -> {q5_10.value}")
                    
                    context = 'predictors_included' if self._is_weak_or_ni(q5_6) else 'predictors_not_included'
                    evidence_result = self._assess_evidence_pathway(q5_10, context)
                    return {
                        'risk_level': evidence_result['risk_level'],
                        'pathway': pathway,
                        'rationale': evidence_result['rationale']
                    }
            
            elif q5_5 in [Response.WEAK_YES, Response.NO_INFORMATION]:
                # WY/NI -> Q5.10
                q5_10 = responses.get('q5_10_evidence_not_biased')
                pathway.append("WY/NI path -> Proceeding to Q5.10")
                if q5_10:
                    pathway.append(f"Q5.10 Evidence that result is not biased? -> {q5_10.value}")
                
                evidence_result = self._assess_evidence_pathway(q5_10, 'exclusion_somewhat_related')
                return {
                    'risk_level': evidence_result['risk_level'],
                    'pathway': pathway,
                    'rationale': evidence_result['rationale']
                }
            
            elif q5_5 == Response.STRONG_YES:
                # SY -> Q5.10
                q5_10 = responses.get('q5_10_evidence_not_biased')
                pathway.append("SY path -> Proceeding to Q5.10")
                if q5_10:
                    pathway.append(f"Q5.10 Evidence that result is not biased? -> {q5_10.value}")
                
                evidence_result = self._assess_evidence_pathway(q5_10, 'exclusion_related')
                return {
                    'risk_level': evidence_result['risk_level'],
                    'pathway': pathway,
                    'rationale': evidence_result['rationale']
                }
        
        # Analysis based on imputing missing values path
        elif self._is_negative_response(q5_4):
            # N/PN -> Q5.7
            q5_7 = responses.get('q5_7_analysis_imputing')
            if not q5_7:
                return {
                    'risk_level': RiskLevel.HIGH_RISK,
                    'pathway': pathway + ["Missing Q5.7 response"],
                    'rationale': 'incomplete_imputation_assessment'
                }
            
            pathway.append(f"Q5.7 Analysis based on imputing missing values? -> {q5_7.value}")
            
            if self._is_positive_response(q5_7):
                # Y/PY -> Q5.8
                q5_8 = responses.get('q5_8_appropriate_imputation')
                if not q5_8:
                    return {
                        'risk_level': RiskLevel.HIGH_RISK,
                        'pathway': pathway + ["Missing Q5.8 response"],
                        'rationale': 'incomplete_imputation_quality_assessment'
                    }
                
                pathway.append(f"Q5.8 Appropriate imputation? -> {q5_8.value}")
                
                # All Q5.8 responses lead to Q5.10
                q5_10 = responses.get('q5_10_evidence_not_biased')
                pathway.append("Proceeding to Q5.10")
                if q5_10:
                    pathway.append(f"Q5.10 Evidence that result is not biased? -> {q5_10.value}")
                
                context = 'appropriate_imputation' if self._is_positive_response(q5_8) else 'poor_imputation'
                evidence_result = self._assess_evidence_pathway(q5_10, context)
                return {
                    'risk_level': evidence_result['risk_level'],
                    'pathway': pathway,
                    'rationale': evidence_result['rationale']
                }
            
            elif self._is_negative_response(q5_7):
                # N/PN -> Q5.9
                q5_9 = responses.get('q5_9_appropriate_method')
                if not q5_9:
                    return {
                        'risk_level': RiskLevel.HIGH_RISK,
                        'pathway': pathway + ["Missing Q5.9 response"],
                        'rationale': 'incomplete_method_assessment'
                    }
                
                pathway.append(f"Q5.9 Appropriate method? -> {q5_9.value}")
                
                # All Q5.9 responses lead to Q5.10
                q5_10 = responses.get('q5_10_evidence_not_biased')
                pathway.append("Proceeding to Q5.10")
                if q5_10:
                    pathway.append(f"Q5.10 Evidence that result is not biased? -> {q5_10.value}")
                
                context = 'appropriate_method' if self._is_positive_response(q5_9) else 'poor_method'
                evidence_result = self._assess_evidence_pathway(q5_10, context)
                return {
                    'risk_level': evidence_result['risk_level'],
                    'pathway': pathway,
                    'rationale': evidence_result['rationale']
                }
        
        # Default fallback
        return {
            'risk_level': RiskLevel.HIGH_RISK,
            'pathway': pathway + ["Unexpected pathway - defaulting to HIGH RISK"],
            'rationale': 'unexpected_pathway'
        }

    def get_detailed_assessment(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Get detailed assessment with additional context about missing data handling
        """
        result = self.assess_missing_data_bias(responses)
        
        # Add detailed explanations based on rationale
        explanations = {
            'complete_data_all_participants': 
                "Complete data available for all participants across all relevant variables. "
                "This eliminates missing data bias.",
            
            'predictors_included_strong': 
                "Complete case analysis was used, but strong evidence that predictors of "
                "missingness were included in the model, reducing bias risk.",
            
            'appropriate_imputation': 
                "Missing data were handled using imputation methods, with evidence of "
                "appropriate imputation techniques.",
            
            'poor_imputation': 
                "Missing data were handled using imputation, but the imputation methods "
                "may not be appropriate, creating potential bias.",
            
            'exclusion_related': 
                "Exclusions from analysis appear related to the true outcome value, "
                "creating substantial risk of bias.",
            
            'incomplete_data_assessment': 
                "Insufficient information to assess completeness of data."
        }
        
        result['explanation'] = explanations.get(
            result['rationale'], 
            f"Assessment based on: {result['rationale']}"
        )
        
        # Add missing data strategy assessment
        missing_data_strategies = []
        
        if responses.get('q5_4_complete_case_analysis') in [Response.YES, Response.PROBABLY_YES]:
            missing_data_strategies.append("Complete case analysis")
        
        if responses.get('q5_7_analysis_imputing') in [Response.YES, Response.PROBABLY_YES]:
            missing_data_strategies.append("Imputation methods")
            
        if responses.get('q5_6_predictors_missingness') in [Response.YES, Response.PROBABLY_YES, Response.STRONG_YES]:
            missing_data_strategies.append("Predictors of missingness modeled")
        
        result['missing_data_strategies'] = missing_data_strategies
        
        return result

    def get_questions(self) -> Dict[str, str]:
        """Return the algorithm questions"""
        return self.questions.copy()

# Example usage and testing
if __name__ == "__main__":
    robins_e_d5 = ROBINSEDomain5()
    
    # Example 1: Low risk - complete data
    responses_low = {
        'q5_1_to_5_3_complete_data': Response.YES
    }
    
    result_low = robins_e_d5.get_detailed_assessment(responses_low)
    print("=== Low Risk Example ===")
    print(f"Risk Level: {result_low['risk_level'].value}")
    print(f"Rationale: {result_low['rationale']}")
    print(f"Explanation: {result_low['explanation']}")
    print(f"Strategies: {result_low['missing_data_strategies']}")
    print()
    
    # Example 2: Some concerns - good predictors included
    responses_concerns = {
        'q5_1_to_5_3_complete_data': Response.NO,
        'q5_4_complete_case_analysis': Response.YES,
        'q5_5_exclusion_related_outcome': Response.NO,
        'q5_6_predictors_missingness': Response.STRONG_YES
    }
    
    result_concerns = robins_e_d5.get_detailed_assessment(responses_concerns)
    print("=== Some Concerns Example ===")
    print(f"Risk Level: {result_concerns['risk_level'].value}")
    print(f"Rationale: {result_concerns['rationale']}")
    print(f"Explanation: {result_concerns['explanation']}")
    print(f"Strategies: {result_concerns['missing_data_strategies']}")
    print()
    
    # Example 3: High risk - imputation issues
    responses_high = {
        'q5_1_to_5_3_complete_data': Response.NO,
        'q5_4_complete_case_analysis': Response.NO,
        'q5_7_analysis_imputing': Response.YES,
        'q5_8_appropriate_imputation': Response.STRONG_NO,
        'q5_10_evidence_not_biased': Response.NO
    }
    
    result_high = robins_e_d5.get_detailed_assessment(responses_high)
    print("=== High Risk Example ===")
    print(f"Risk Level: {result_high['risk_level'].value}")
    print(f"Rationale: {result_high['rationale']}")
    print(f"Explanation: {result_high['explanation']}")
    print(f"Strategies: {result_high['missing_data_strategies']}")
    print()
    
    # Example 4: Complex pathway - exclusion related but evidence against bias
    responses_complex = {
        'q5_1_to_5_3_complete_data': Response.NO,
        'q5_4_complete_case_analysis': Response.YES,
        'q5_5_exclusion_related_outcome': Response.STRONG_YES,
        'q5_10_evidence_not_biased': Response.YES
    }
    
    result_complex = robins_e_d5.get_detailed_assessment(responses_complex)
    print("=== Complex Pathway Example ===")
    print(f"Risk Level: {result_complex['risk_level'].value}")
    print(f"Rationale: {result_complex['rationale']}")
    print(f"Explanation: {result_complex['explanation']}")
    print(f"Strategies: {result_complex['missing_data_strategies']}")
    print()
    
    # Print available questions for reference
    print("=== Available Questions ===")
    for key, question in robins_e_d5.get_questions().items():
        print(f"{key}: {question}")
