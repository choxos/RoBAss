#!/usr/bin/env python3
"""
Test script to validate the RoB 2.0 assessment engine
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, '/Users/choxos/Documents/GitHub/RoBAss')

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robass_project.settings')
django.setup()

from assessments.rob2_engine import (
    assess_domain_1_randomization,
    assess_domain_2_deviations,
    assess_domain_3_missing_data,
    assess_domain_4_outcome_measurement,
    assess_domain_5_selective_reporting,
    assess_overall_rob2,
    calculate_rob2_assessment
)


def test_domain_1():
    """Test Domain 1: Randomization process"""
    print("\n=== Testing Domain 1: Randomization Process ===")
    
    # Test case: Low risk
    risk, reason = assess_domain_1_randomization('Y', 'Y', 'N')
    print(f"Low risk case: {risk} - {reason}")
    assert risk == 'Low'
    
    # Test case: High risk
    risk, reason = assess_domain_1_randomization('N', 'N', 'Y')
    print(f"High risk case: {risk} - {reason}")
    assert risk == 'High'
    
    # Test case: Some concerns
    risk, reason = assess_domain_1_randomization('Y', 'Y', 'PY')
    print(f"Some concerns case: {risk} - {reason}")
    assert risk == 'Some concerns'
    
    print("✓ Domain 1 tests passed")


def test_domain_2():
    """Test Domain 2: Deviations from intended interventions"""
    print("\n=== Testing Domain 2: Deviations ===")
    
    # Test case: Low risk (double-blind, ITT)
    risk, reason, details = assess_domain_2_deviations('N', 'N', 'NA', 'NA', 'NA', 'Y', 'NA')
    print(f"Low risk case: {risk} - {reason}")
    assert risk == 'Low'
    
    # Test case: High risk (unbalanced deviations)
    risk, reason, details = assess_domain_2_deviations('Y', 'Y', 'Y', 'Y', 'N', 'Y', 'NA')
    print(f"High risk case: {risk} - {reason}")
    assert risk == 'High'
    
    print("✓ Domain 2 tests passed")


def test_domain_3():
    """Test Domain 3: Missing outcome data"""
    print("\n=== Testing Domain 3: Missing Data ===")
    
    # Test case: Low risk (complete data)
    risk, reason = assess_domain_3_missing_data('Y', 'NA', 'NA', 'NA')
    print(f"Low risk case: {risk} - {reason}")
    assert risk == 'Low'
    
    # Test case: High risk (missing data likely depends on outcome)
    risk, reason = assess_domain_3_missing_data('N', 'N', 'Y', 'Y')
    print(f"High risk case: {risk} - {reason}")
    assert risk == 'High'
    
    print("✓ Domain 3 tests passed")


def test_domain_4():
    """Test Domain 4: Outcome measurement"""
    print("\n=== Testing Domain 4: Outcome Measurement ===")
    
    # Test case: Low risk (blinded assessors)
    risk, reason = assess_domain_4_outcome_measurement('N', 'N', 'N', 'NA', 'NA')
    print(f"Low risk case: {risk} - {reason}")
    assert risk == 'Low'
    
    # Test case: High risk (inappropriate method)
    risk, reason = assess_domain_4_outcome_measurement('Y', 'NA', 'NA', 'NA', 'NA')
    print(f"High risk case: {risk} - {reason}")
    assert risk == 'High'
    
    print("✓ Domain 4 tests passed")


def test_domain_5():
    """Test Domain 5: Selective reporting"""
    print("\n=== Testing Domain 5: Selective Reporting ===")
    
    # Test case: Low risk (pre-specified plan)
    risk, reason = assess_domain_5_selective_reporting('Y', 'N', 'N')
    print(f"Low risk case: {risk} - {reason}")
    assert risk == 'Low'
    
    # Test case: High risk (result selection)
    risk, reason = assess_domain_5_selective_reporting('N', 'Y', 'N')
    print(f"High risk case: {risk} - {reason}")
    assert risk == 'High'
    
    print("✓ Domain 5 tests passed")


def test_overall_assessment():
    """Test overall RoB 2 assessment logic"""
    print("\n=== Testing Overall Assessment ===")
    
    # Test case: All low risk
    risk, reason = assess_overall_rob2('Low', 'Low', 'Low', 'Low', 'Low')
    print(f"All low risk: {risk} - {reason}")
    assert risk == 'Low'
    
    # Test case: One high risk
    risk, reason = assess_overall_rob2('High', 'Low', 'Low', 'Low', 'Low')
    print(f"One high risk: {risk} - {reason}")
    assert risk == 'High'
    
    # Test case: Multiple some concerns
    risk, reason = assess_overall_rob2('Some concerns', 'Some concerns', 'Some concerns', 'Low', 'Low')
    print(f"Multiple some concerns: {risk} - {reason}")
    assert risk == 'High'
    
    # Test case: Few some concerns
    risk, reason = assess_overall_rob2('Some concerns', 'Some concerns', 'Low', 'Low', 'Low')
    print(f"Few some concerns: {risk} - {reason}")
    assert risk == 'Some concerns'
    
    print("✓ Overall assessment tests passed")


def test_full_assessment():
    """Test complete assessment with real response data"""
    print("\n=== Testing Full Assessment ===")
    
    # Example responses for a typical RCT
    responses = {
        '1.1': 'Y',   # Random sequence
        '1.2': 'Y',   # Allocation concealed
        '1.3': 'N',   # No baseline imbalances
        '2.1': 'N',   # Participants blinded
        '2.2': 'N',   # Personnel blinded  
        '2.3': 'NA',  # No deviations (blinded)
        '2.4': 'NA',
        '2.5': 'NA',
        '2.6': 'Y',   # Appropriate analysis
        '2.7': 'NA',
        '3.1': 'Y',   # Complete data
        '3.2': 'NA',
        '3.3': 'NA',
        '3.4': 'NA',
        '4.1': 'N',   # Appropriate measurement
        '4.2': 'N',   # Consistent measurement
        '4.3': 'N',   # Blinded assessors
        '4.4': 'NA',
        '4.5': 'NA',
        '5.1': 'Y',   # Pre-specified plan
        '5.2': 'N',   # No outcome selection
        '5.3': 'N'    # No analysis selection
    }
    
    results = calculate_rob2_assessment(responses)
    
    print(f"Domain 1: {results['domain_1']['risk']} - {results['domain_1']['reasoning']}")
    print(f"Domain 2: {results['domain_2']['risk']} - {results['domain_2']['reasoning']}")
    print(f"Domain 3: {results['domain_3']['risk']} - {results['domain_3']['reasoning']}")
    print(f"Domain 4: {results['domain_4']['risk']} - {results['domain_4']['reasoning']}")
    print(f"Domain 5: {results['domain_5']['risk']} - {results['domain_5']['reasoning']}")
    print(f"Overall: {results['overall']['risk']} - {results['overall']['reasoning']}")
    
    # Should be all low risk for this ideal study
    assert results['overall']['risk'] == 'Low'
    assert all(results[f'domain_{i}']['risk'] == 'Low' for i in range(1, 6))
    
    print("✓ Full assessment test passed")


if __name__ == '__main__':
    print("Testing RoB 2.0 Assessment Engine")
    print("=" * 50)
    
    try:
        test_domain_1()
        test_domain_2()
        test_domain_3()
        test_domain_4()
        test_domain_5()
        test_overall_assessment()
        test_full_assessment()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! RoB 2.0 engine is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
