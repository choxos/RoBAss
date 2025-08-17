"""
ROBINS-E Assessment Engine for Risk of Bias in Non-randomized Studies of Exposure

This module implements the complete ROBINS-E assessment algorithms based on the
official ROBINS-E methodology for observational studies of exposures.
"""

import sys
import os

# Add the algorithms directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'algorithms', 'robins_e_2'))

from robins_e_domain1 import ROBINSEDomain1, Response
from robins_e_domain2 import ROBINSEDomain2
from robins_e_domain3 import ROBINSEDomain3
from robins_e_domain4 import ROBINSEDomain4
from robins_e_domain5 import ROBINSEDomain5
from robins_e_domain6 import ROBINSEDomain6
from robins_e_domain7 import ROBINSEDomain7
from robins_e_overall import ROBINSEOverallAssessment, DomainRisk, OverallRisk, ConclusionThreat

from typing import Dict, Any, List, Tuple
from enum import Enum


class ROBINSERiskLevel(Enum):
    """ROBINS-E specific risk levels"""
    LOW_RISK = "Low risk of bias (except for concerns about uncontrolled confounding)"
    SOME_CONCERNS = "Some concerns"
    HIGH_RISK = "High risk of bias"
    VERY_HIGH_RISK = "Very high risk of bias"


class ROBINSEEngine:
    """Main engine for ROBINS-E assessments"""
    
    def __init__(self):
        self.domain1 = ROBINSEDomain1()
        self.domain2 = ROBINSEDomain2()
        self.domain3 = ROBINSEDomain3()
        self.domain4 = ROBINSEDomain4()
        self.domain5 = ROBINSEDomain5()
        self.domain6 = ROBINSEDomain6()
        self.domain7 = ROBINSEDomain7()
        self.overall_assessor = ROBINSEOverallAssessment()
        
        self.domain_names = {
            'domain_1': 'Risk of bias due to confounding',
            'domain_2': 'Risk of bias in measurement of exposures',
            'domain_3': 'Risk of bias in selection of participants into the study',
            'domain_4': 'Risk of bias due to post-exposure interventions',
            'domain_5': 'Risk of bias due to missing data',
            'domain_6': 'Risk of bias in measurement of outcomes',
            'domain_7': 'Risk of bias in selection of the reported result'
        }

    def _convert_response(self, response: str) -> Response:
        """Convert string response to Response enum"""
        response_mapping = {
            'yes': Response.YES,
            'probably_yes': Response.PROBABLY_YES,
            'no': Response.NO,
            'probably_no': Response.PROBABLY_NO,
            'no_information': Response.NO_INFORMATION,
            'not_applicable': Response.NO_INFORMATION  # Map to NI for simplicity
        }
        
        response_lower = response.lower()
        if response_lower in response_mapping:
            return response_mapping[response_lower]
        else:
            # Try direct enum mapping for abbreviations
            try:
                return Response(response.upper())
            except ValueError:
                raise ValueError(f"Invalid response: {response}")

    def _convert_responses_dict(self, responses: Dict[str, str]) -> Dict[str, Response]:
        """Convert dictionary of string responses to Response enums"""
        return {key: self._convert_response(value) for key, value in responses.items()}

    def assess_domain_1_confounding(self, responses: Dict[str, str], variant: str = 'B') -> Dict[str, Any]:
        """
        Assess Domain 1: Risk of bias due to confounding
        
        Args:
            responses: Dictionary of responses to signalling questions
            variant: 'A' or 'B' algorithm variant
            
        Returns:
            Assessment result with risk level and reasoning
        """
        try:
            converted_responses = self._convert_responses_dict(responses)
            result = self.domain1.assess_bias_risk(converted_responses, variant)
            
            return {
                'domain': 'Domain 1: Confounding',
                'risk_level': result['risk_level'].value,
                'pathway': result['pathway'],
                'variant_used': result['variant'],
                'responses': responses
            }
        except Exception as e:
            return {
                'domain': 'Domain 1: Confounding',
                'risk_level': 'High risk of bias',
                'error': str(e),
                'responses': responses
            }

    def assess_domain_2_exposure_measurement(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Assess Domain 2: Risk of bias in measurement of exposures
        
        Args:
            responses: Dictionary of responses to signalling questions
            
        Returns:
            Assessment result with risk level and reasoning
        """
        try:
            converted_responses = self._convert_responses_dict(responses)
            result = self.domain2.assess_bias_risk(converted_responses)
            
            return {
                'domain': 'Domain 2: Measurement of Exposures',
                'risk_level': result['risk_level'].value,
                'pathway': result['pathway'],
                'responses': responses
            }
        except Exception as e:
            return {
                'domain': 'Domain 2: Measurement of Exposures',
                'risk_level': 'High risk of bias',
                'error': str(e),
                'responses': responses
            }

    def assess_domain_3_selection(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Assess Domain 3: Risk of bias in selection of participants into the study
        
        Args:
            responses: Dictionary of responses to signalling questions
            
        Returns:
            Assessment result with risk level and reasoning
        """
        try:
            converted_responses = self._convert_responses_dict(responses)
            result = self.domain3.assess_bias_risk(converted_responses)
            
            return {
                'domain': 'Domain 3: Selection of Participants',
                'risk_level': result['risk_level'].value,
                'pathway': result['pathway'],
                'responses': responses
            }
        except Exception as e:
            return {
                'domain': 'Domain 3: Selection of Participants',
                'risk_level': 'High risk of bias',
                'error': str(e),
                'responses': responses
            }

    def assess_domain_4_post_exposure_interventions(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Assess Domain 4: Risk of bias due to post-exposure interventions
        
        Args:
            responses: Dictionary of responses to signalling questions
            
        Returns:
            Assessment result with risk level and reasoning
        """
        try:
            converted_responses = self._convert_responses_dict(responses)
            result = self.domain4.assess_bias_risk(converted_responses)
            
            return {
                'domain': 'Domain 4: Post-exposure Interventions',
                'risk_level': result['risk_level'].value,
                'pathway': result['pathway'],
                'responses': responses
            }
        except Exception as e:
            return {
                'domain': 'Domain 4: Post-exposure Interventions',
                'risk_level': 'High risk of bias',
                'error': str(e),
                'responses': responses
            }

    def assess_domain_5_missing_data(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Assess Domain 5: Risk of bias due to missing data
        
        Args:
            responses: Dictionary of responses to signalling questions
            
        Returns:
            Assessment result with risk level and reasoning
        """
        try:
            converted_responses = self._convert_responses_dict(responses)
            result = self.domain5.assess_bias_risk(converted_responses)
            
            return {
                'domain': 'Domain 5: Missing Data',
                'risk_level': result['risk_level'].value,
                'pathway': result['pathway'],
                'responses': responses
            }
        except Exception as e:
            return {
                'domain': 'Domain 5: Missing Data',
                'risk_level': 'High risk of bias',
                'error': str(e),
                'responses': responses
            }

    def assess_domain_6_outcome_measurement(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Assess Domain 6: Risk of bias in measurement of outcomes
        
        Args:
            responses: Dictionary of responses to signalling questions
            
        Returns:
            Assessment result with risk level and reasoning
        """
        try:
            converted_responses = self._convert_responses_dict(responses)
            result = self.domain6.assess_bias_risk(converted_responses)
            
            return {
                'domain': 'Domain 6: Measurement of Outcomes',
                'risk_level': result['risk_level'].value,
                'pathway': result['pathway'],
                'responses': responses
            }
        except Exception as e:
            return {
                'domain': 'Domain 6: Measurement of Outcomes',
                'risk_level': 'High risk of bias',
                'error': str(e),
                'responses': responses
            }

    def assess_domain_7_reported_result(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Assess Domain 7: Risk of bias in selection of the reported result
        
        Args:
            responses: Dictionary of responses to signalling questions
            
        Returns:
            Assessment result with risk level and reasoning
        """
        try:
            converted_responses = self._convert_responses_dict(responses)
            result = self.domain7.assess_bias_risk(converted_responses)
            
            return {
                'domain': 'Domain 7: Selection of Reported Result',
                'risk_level': result['risk_level'].value,
                'pathway': result['pathway'],
                'responses': responses
            }
        except Exception as e:
            return {
                'domain': 'Domain 7: Selection of Reported Result',
                'risk_level': 'High risk of bias',
                'error': str(e),
                'responses': responses
            }

    def assess_overall_bias(self, domain_assessments: Dict[str, str]) -> Dict[str, Any]:
        """
        Assess overall risk of bias combining all domain assessments
        
        Args:
            domain_assessments: Dictionary mapping domain names to risk levels
            
        Returns:
            Overall assessment result
        """
        try:
            result = self.overall_assessor.assess_overall_bias_risk(domain_assessments)
            
            return {
                'overall_risk': result['overall_risk'].value,
                'rationale': result['rationale'],
                'domain_assessments': result['domain_assessments'],
                'risk_counts': result['risk_counts'],
                'contributing_domains': result.get('contributing_domains', [])
            }
        except Exception as e:
            return {
                'overall_risk': 'High risk of bias',
                'error': str(e),
                'domain_assessments': domain_assessments
            }

    def complete_assessment(self, all_responses: Dict[str, Dict[str, str]], 
                          domain_1_variant: str = 'B') -> Dict[str, Any]:
        """
        Complete full ROBINS-E assessment for all domains
        
        Args:
            all_responses: Dictionary with responses for each domain
            domain_1_variant: Variant to use for Domain 1 assessment
            
        Returns:
            Complete assessment results
        """
        results = {}
        
        # Assess each domain
        domain_methods = [
            ('domain_1', self.assess_domain_1_confounding),
            ('domain_2', self.assess_domain_2_exposure_measurement),
            ('domain_3', self.assess_domain_3_selection),
            ('domain_4', self.assess_domain_4_post_exposure_interventions),
            ('domain_5', self.assess_domain_5_missing_data),
            ('domain_6', self.assess_domain_6_outcome_measurement),
            ('domain_7', self.assess_domain_7_reported_result)
        ]
        
        domain_risk_levels = {}
        
        for domain_key, method in domain_methods:
            if domain_key in all_responses:
                if domain_key == 'domain_1':
                    domain_result = method(all_responses[domain_key], domain_1_variant)
                else:
                    domain_result = method(all_responses[domain_key])
                
                results[domain_key] = domain_result
                domain_risk_levels[domain_key] = domain_result['risk_level']
            else:
                results[domain_key] = {
                    'domain': self.domain_names[domain_key],
                    'error': 'No responses provided for this domain'
                }
        
        # Assess overall risk if we have domain assessments
        if domain_risk_levels:
            overall_result = self.assess_overall_bias(domain_risk_levels)
            results['overall'] = overall_result
        
        return results

    def get_signalling_questions(self, domain: str) -> List[Dict[str, str]]:
        """
        Get signalling questions for a specific domain
        
        Args:
            domain: Domain identifier (e.g., 'domain_1')
            
        Returns:
            List of questions with their identifiers
        """
        domain_questions = {
            'domain_1': self.domain1.questions,
            'domain_2': self.domain2.questions if hasattr(self.domain2, 'questions') else {},
            'domain_3': self.domain3.questions if hasattr(self.domain3, 'questions') else {},
            'domain_4': self.domain4.questions if hasattr(self.domain4, 'questions') else {},
            'domain_5': self.domain5.questions if hasattr(self.domain5, 'questions') else {},
            'domain_6': self.domain6.questions if hasattr(self.domain6, 'questions') else {},
            'domain_7': self.domain7.questions if hasattr(self.domain7, 'questions') else {},
        }
        
        questions = domain_questions.get(domain, {})
        return [{'id': key, 'text': value} for key, value in questions.items()]

    def get_domain_info(self) -> Dict[str, str]:
        """Get information about all ROBINS-E domains"""
        return self.domain_names.copy()


# Example usage and testing functions
def test_robins_e_engine():
    """Test the ROBINS-E engine with example data"""
    engine = ROBINSEEngine()
    
    # Example responses for Domain 1 (Confounding)
    domain_1_responses = {
        'q1_1_appropriate_method': 'yes',
        'q1_2_controlled_important': 'yes',
        'q1_3_factors_measured': 'yes',
        'q1_5_negative_controls': 'no'
    }
    
    # Test Domain 1 assessment
    result = engine.assess_domain_1_confounding(domain_1_responses, variant='B')
    print("=== ROBINS-E Domain 1 Test ===")
    print(f"Domain: {result['domain']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Variant Used: {result['variant_used']}")
    if 'pathway' in result:
        print(f"Pathway: {' -> '.join(result['pathway'])}")
    print()
    
    # Test overall assessment with example domain results
    domain_assessments = {
        'domain_1': 'Low risk of bias (except for concerns about uncontrolled confounding)',
        'domain_2': 'Some concerns',
        'domain_3': 'Low risk of bias',
        'domain_4': 'Low risk of bias',
        'domain_5': 'Low risk of bias',
        'domain_6': 'Low risk of bias',
        'domain_7': 'Low risk of bias'
    }
    
    overall_result = engine.assess_overall_bias(domain_assessments)
    print("=== ROBINS-E Overall Assessment Test ===")
    print(f"Overall Risk: {overall_result['overall_risk']}")
    print(f"Rationale: {overall_result['rationale']}")
    print(f"Contributing Domains: {overall_result.get('contributing_domains', [])}")
    print()


if __name__ == "__main__":
    test_robins_e_engine()
