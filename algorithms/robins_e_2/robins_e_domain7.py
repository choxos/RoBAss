"""
ROBINS-E Tool Domain 7: Risk of Bias in Reported Results
Implementation of the algorithm for assessing selective reporting and multiple testing bias
"""

from enum import Enum
from typing import Dict, Any, List

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
    VERY_HIGH_RISK = "Very high risk of bias"

class ROBINSEDomain7:
    """ROBINS-E Domain 7 Algorithm Implementation"""
    
    def __init__(self):
        self.questions = {
            'q7_1_result_according_plan': "7.1 Result reported according to analysis plan?",
            'q7_2_multiple_exposure_measurements': "7.2 Result selected from multiple exposure measurements?",
            'q7_3_multiple_outcome_measurements': "7.3 Result selected from multiple outcome measurements?",
            'q7_4_multiple_analyses': "7.4 Result selected from multiple analyses of the data?",
            'q7_5_multiple_subgroups': "7.5 Result selected from multiple subgroups?"
        }
        
        self.selection_questions = [
            'q7_2_multiple_exposure_measurements',
            'q7_3_multiple_outcome_measurements', 
            'q7_4_multiple_analyses',
            'q7_5_multiple_subgroups'
        ]
    
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

    def _assess_selection_bias(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Assess selective reporting bias based on Q7.2-7.5 responses
        
        Returns:
            Dictionary with risk assessment and selection details
        """
        selection_responses = {}
        positive_count = 0
        ni_count = 0
        negative_count = 0
        
        # Collect responses for selection questions
        for question in self.selection_questions:
            response = responses.get(question)
            if response:
                selection_responses[question] = response
                
                if self._is_positive_response(response):
                    positive_count += 1
                elif self._is_no_information(response):
                    ni_count += 1
                elif self._is_negative_response(response):
                    negative_count += 1
        
        # Determine risk level based on combination rules
        total_questions = len(self.selection_questions)
        answered_questions = len(selection_responses)
        
        # Check if all questions were answered
        if answered_questions < total_questions:
            missing_questions = [q for q in self.selection_questions if q not in selection_responses]
            return {
                'risk_level': RiskLevel.SOME_CONCERNS,
                'rationale': 'incomplete_selection_assessment',
                'positive_count': positive_count,
                'ni_count': ni_count,
                'negative_count': negative_count,
                'missing_questions': missing_questions,
                'selection_responses': selection_responses
            }
        
        # Apply combination rules from flowchart
        if positive_count == 0 and ni_count == 0:
            # All N/PN -> LOW RISK
            return {
                'risk_level': RiskLevel.LOW_RISK,
                'rationale': 'no_selective_reporting',
                'positive_count': positive_count,
                'ni_count': ni_count,
                'negative_count': negative_count,
                'selection_responses': selection_responses
            }
        
        elif positive_count == 0 and ni_count > 0:
            # At least one NI, but none Y/PY -> SOME CONCERNS
            return {
                'risk_level': RiskLevel.SOME_CONCERNS,
                'rationale': 'unclear_selective_reporting',
                'positive_count': positive_count,
                'ni_count': ni_count,
                'negative_count': negative_count,
                'selection_responses': selection_responses
            }
        
        elif positive_count <= 2:
            # Up to two Y/PY -> HIGH RISK
            return {
                'risk_level': RiskLevel.HIGH_RISK,
                'rationale': 'moderate_selective_reporting',
                'positive_count': positive_count,
                'ni_count': ni_count,
                'negative_count': negative_count,
                'selection_responses': selection_responses
            }
        
        else:  # positive_count > 2
            # More than two Y/PY -> VERY HIGH RISK
            return {
                'risk_level': RiskLevel.VERY_HIGH_RISK,
                'rationale': 'extensive_selective_reporting',
                'positive_count': positive_count,
                'ni_count': ni_count,
                'negative_count': negative_count,
                'selection_responses': selection_responses
            }

    def assess_reported_results_bias(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Assess risk of bias in reported results
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with risk assessment and pathway taken
        """
        pathway = []
        
        # Start with Q7.1 Result reported according to analysis plan?
        q7_1 = responses.get('q7_1_result_according_plan')
        if not q7_1:
            return {
                'risk_level': RiskLevel.SOME_CONCERNS,
                'pathway': ["Missing Q7.1 response"],
                'rationale': 'incomplete_plan_adherence_assessment'
            }
        
        pathway.append(f"Q7.1 Result reported according to analysis plan? -> {q7_1.value}")
        
        # Direct path to LOW RISK if results according to plan
        if self._is_positive_response(q7_1):
            pathway.append("Y/PY path -> LOW RISK OF BIAS")
            return {
                'risk_level': RiskLevel.LOW_RISK,
                'pathway': pathway,
                'rationale': 'results_according_to_plan'
            }
        
        # N/PN/NI path -> assess selective reporting
        pathway.append("N/PN/NI path -> Assessing selective reporting")
        
        # Assess selection bias using Q7.2-7.5
        selection_assessment = self._assess_selection_bias(responses)
        
        # Add selection details to pathway
        pathway.append(f"Selection assessment: {selection_assessment['positive_count']} positive, "
                      f"{selection_assessment['ni_count']} no information, "
                      f"{selection_assessment['negative_count']} negative")
        
        return {
            'risk_level': selection_assessment['risk_level'],
            'pathway': pathway,
            'rationale': selection_assessment['rationale'],
            'positive_count': selection_assessment['positive_count'],
            'ni_count': selection_assessment['ni_count'],
            'negative_count': selection_assessment['negative_count'],
            'selection_responses': selection_assessment.get('selection_responses', {}),
            'missing_questions': selection_assessment.get('missing_questions', [])
        }

    def get_detailed_assessment(self, responses: Dict[str, Response]) -> Dict[str, Any]:
        """
        Get detailed assessment with additional context about reporting bias
        
        Args:
            responses: Dictionary containing responses to algorithm questions
            
        Returns:
            Dictionary with detailed risk assessment and explanations
        """
        result = self.assess_reported_results_bias(responses)
        
        # Add detailed explanations based on rationale
        explanations = {
            'results_according_to_plan': 
                "Results were reported according to a pre-specified analysis plan, minimizing "
                "the risk of selective reporting bias. This represents best practice for "
                "transparent research conduct.",
            
            'no_selective_reporting': 
                "No evidence of selective reporting from multiple exposure measurements, "
                "outcome measurements, analyses, or subgroups. Results appear to be "
                "comprehensively reported.",
            
            'unclear_selective_reporting': 
                "Some uncertainty about selective reporting practices, but no clear evidence "
                "of selection from multiple alternatives. This may reflect incomplete "
                "documentation rather than bias.",
            
            'moderate_selective_reporting': 
                "Evidence of selective reporting from a limited number of alternatives "
                "(exposure measurements, outcome measurements, analyses, or subgroups). "
                "This creates substantial bias risk.",
            
            'extensive_selective_reporting': 
                "Extensive evidence of selective reporting across multiple domains "
                "(exposure measurements, outcome measurements, analyses, and subgroups). "
                "This represents severe bias that undermines result reliability.",
            
            'incomplete_plan_adherence_assessment': 
                "Insufficient information to assess whether results were reported according "
                "to a pre-specified analysis plan.",
            
            'incomplete_selection_assessment': 
                "Insufficient information to fully assess selective reporting practices."
        }
        
        result['explanation'] = explanations.get(
            result['rationale'], 
            f"Assessment based on: {result['rationale']}"
        )
        
        # Add selective reporting details
        if 'selection_responses' in result:
            reporting_issues = self._identify_reporting_issues(result['selection_responses'])
            result['reporting_issues'] = reporting_issues
        
        # Add bias severity assessment
        bias_severity = self._assess_bias_severity(result)
        result['bias_severity'] = bias_severity
        
        return result

    def _identify_reporting_issues(self, selection_responses: Dict[str, Response]) -> List[str]:
        """Identify specific types of selective reporting"""
        issues = []
        
        issue_mapping = {
            'q7_2_multiple_exposure_measurements': "Selection from multiple exposure measurements",
            'q7_3_multiple_outcome_measurements': "Selection from multiple outcome measurements", 
            'q7_4_multiple_analyses': "Selection from multiple analyses",
            'q7_5_multiple_subgroups': "Selection from multiple subgroups"
        }
        
        for question, response in selection_responses.items():
            if self._is_positive_response(response):
                issues.append(issue_mapping.get(question, f"Issue with {question}"))
            elif self._is_no_information(response):
                issues.append(f"Unclear: {issue_mapping.get(question, question)}")
        
        return issues

    def _assess_bias_severity(self, result: Dict[str, Any]) -> str:
        """Assess the severity and impact of reporting bias"""
        risk_level = result['risk_level']
        positive_count = result.get('positive_count', 0)
        
        if risk_level == RiskLevel.LOW_RISK:
            return "Minimal impact on result reliability"
        elif risk_level == RiskLevel.SOME_CONCERNS:
            return "Moderate uncertainty about result selection"
        elif risk_level == RiskLevel.HIGH_RISK:
            if positive_count == 1:
                return "Substantial bias from single domain of selective reporting"
            else:
                return "Substantial bias from multiple domains of selective reporting"
        elif risk_level == RiskLevel.VERY_HIGH_RISK:
            return "Severe bias undermining result credibility"
        
        return "Unknown bias severity"

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
            'recommendations': [],
            'warnings': []
        }
        
        # Check Q7.1
        if 'q7_1_result_according_plan' not in responses:
            validation['is_valid'] = False
            validation['missing_questions'].append('q7_1_result_according_plan')
        else:
            q7_1 = responses['q7_1_result_according_plan']
            
            # If Q7.1 is Y/PY, selection questions not strictly needed
            if self._is_positive_response(q7_1):
                selection_answered = any(q in responses for q in self.selection_questions)
                if selection_answered:
                    validation['recommendations'].append(
                        "Selection questions (Q7.2-7.5) not needed when results follow analysis plan (Q7.1 Y/PY)"
                    )
            else:
                # Q7.2-7.5 are needed for complete assessment
                missing_selection = [q for q in self.selection_questions if q not in responses]
                if missing_selection:
                    validation['warnings'].append(
                        f"Missing selection questions for complete assessment: {missing_selection}"
                    )
                    validation['recommendations'].append(
                        "Consider answering Q7.2-7.5 for comprehensive selective reporting assessment"
                    )
        
        return validation

# Example usage and testing
if __name__ == "__main__":
    robins_e_d7 = ROBINSEDomain7()
    
    # Example 1: Low risk - results according to plan
    responses_low_plan = {
        'q7_1_result_according_plan': Response.YES
    }
    
    result_low_plan = robins_e_d7.get_detailed_assessment(responses_low_plan)
    print("=== Low Risk (According to Plan) Example ===")
    print(f"Risk Level: {result_low_plan['risk_level'].value}")
    print(f"Rationale: {result_low_plan['rationale']}")
    print(f"Bias Severity: {result_low_plan['bias_severity']}")
    print(f"Explanation: {result_low_plan['explanation']}")
    print()
    
    # Example 2: Low risk - no selective reporting
    responses_low_no_selection = {
        'q7_1_result_according_plan': Response.NO,
        'q7_2_multiple_exposure_measurements': Response.NO,
        'q7_3_multiple_outcome_measurements': Response.NO,
        'q7_4_multiple_analyses': Response.NO,
        'q7_5_multiple_subgroups': Response.NO
    }
    
    result_low_no_selection = robins_e_d7.get_detailed_assessment(responses_low_no_selection)
    print("=== Low Risk (No Selection) Example ===")
    print(f"Risk Level: {result_low_no_selection['risk_level'].value}")
    print(f"Rationale: {result_low_no_selection['rationale']}")
    print(f"Positive Count: {result_low_no_selection['positive_count']}")
    print(f"Reporting Issues: {result_low_no_selection['reporting_issues']}")
    print(f"Bias Severity: {result_low_no_selection['bias_severity']}")
    print()
    
    # Example 3: Some concerns - unclear reporting
    responses_concerns = {
        'q7_1_result_according_plan': Response.NO,
        'q7_2_multiple_exposure_measurements': Response.NO,
        'q7_3_multiple_outcome_measurements': Response.NO_INFORMATION,
        'q7_4_multiple_analyses': Response.NO,
        'q7_5_multiple_subgroups': Response.NO_INFORMATION
    }
    
    result_concerns = robins_e_d7.get_detailed_assessment(responses_concerns)
    print("=== Some Concerns Example ===")
    print(f"Risk Level: {result_concerns['risk_level'].value}")
    print(f"Rationale: {result_concerns['rationale']}")
    print(f"NI Count: {result_concerns['ni_count']}")
    print(f"Reporting Issues: {result_concerns['reporting_issues']}")
    print(f"Bias Severity: {result_concerns['bias_severity']}")
    print()
    
    # Example 4: High risk - moderate selective reporting
    responses_high = {
        'q7_1_result_according_plan': Response.NO,
        'q7_2_multiple_exposure_measurements': Response.YES,
        'q7_3_multiple_outcome_measurements': Response.NO,
        'q7_4_multiple_analyses': Response.PROBABLY_YES,
        'q7_5_multiple_subgroups': Response.NO
    }
    
    result_high = robins_e_d7.get_detailed_assessment(responses_high)
    print("=== High Risk Example ===")
    print(f"Risk Level: {result_high['risk_level'].value}")
    print(f"Rationale: {result_high['rationale']}")
    print(f"Positive Count: {result_high['positive_count']}")
    print(f"Reporting Issues: {result_high['reporting_issues']}")
    print(f"Bias Severity: {result_high['bias_severity']}")
    print()
    
    # Example 5: Very high risk - extensive selective reporting
    responses_very_high = {
        'q7_1_result_according_plan': Response.NO,
        'q7_2_multiple_exposure_measurements': Response.YES,
        'q7_3_multiple_outcome_measurements': Response.YES,
        'q7_4_multiple_analyses': Response.YES,
        'q7_5_multiple_subgroups': Response.PROBABLY_YES
    }
    
    result_very_high = robins_e_d7.get_detailed_assessment(responses_very_high)
    print("=== Very High Risk Example ===")
    print(f"Risk Level: {result_very_high['risk_level'].value}")
    print(f"Rationale: {result_very_high['rationale']}")
    print(f"Positive Count: {result_very_high['positive_count']}")
    print(f"Reporting Issues: {result_very_high['reporting_issues']}")
    print(f"Bias Severity: {result_very_high['bias_severity']}")
    print()
    
    # Example 6: Validation check
    incomplete_responses = {
        'q7_1_result_according_plan': Response.NO,
        'q7_2_multiple_exposure_measurements': Response.YES
        # Missing Q7.3-7.5
    }
    
    validation = robins_e_d7.validate_responses(incomplete_responses)
    print("=== Validation Example ===")
    print(f"Is Valid: {validation['is_valid']}")
    print(f"Warnings: {validation['warnings']}")
    print(f"Recommendations: {validation['recommendations']}")
    print()
    
    # Print available questions for reference
    print("=== Available Questions ===")
    for key, question in robins_e_d7.get_questions().items():
        print(f"{key}: {question}")
