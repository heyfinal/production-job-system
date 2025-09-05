#!/usr/bin/env python3
"""
Test script to verify overqualification filtering is working
"""

import asyncio
import json
from intelligent_matcher import IntelligentJobMatcher, CandidateProfile

def test_overqualification_penalties():
    """Test the penalty system with problematic job examples"""
    
    # Initialize matcher
    profile = CandidateProfile()
    matcher = IntelligentJobMatcher(profile)
    
    # Test job that should be heavily penalized
    test_job = {
        'title': 'Senior Business Analyst Manager',
        'company': 'PRICE WATERHOUSE COOPERS',
        'location': 'Dallas, TX',
        'description': 'Lead business analysis team for enterprise clients. MBA preferred.',
        'salary_min': 200000,
        'salary_max': 244000,
        'remote_friendly': False,
        'employment_type': 'FULLTIME',
        'url': 'https://example.com'
    }
    
    print("🔍 Testing Overqualification Filter")
    print("=" * 50)
    print(f"Job: {test_job['title']}")
    print(f"Company: {test_job['company']}")
    print(f"Salary: ${test_job['salary_max']:,}")
    print()
    
    # Calculate match score
    score, reasons = matcher.calculate_match_score(test_job)
    
    print(f"Match Score: {score:.3f}")
    print()
    print("Scoring Breakdown:")
    for reason in reasons:
        if "PENALTY" in reason or "BONUS" in reason:
            print(f"  📌 {reason}")
        else:
            print(f"  • {reason}")
    
    print()
    
    # Check if it would be filtered
    minimum_score = 0.5  # From config.json
    if score < minimum_score:
        print(f"✅ PASSED: Job correctly filtered out (score {score:.3f} < minimum {minimum_score})")
        return True
    else:
        print(f"❌ FAILED: Job should be filtered out but wasn't (score {score:.3f} >= minimum {minimum_score})")
        return False

def test_acceptable_job():
    """Test that acceptable jobs pass through"""
    
    profile = CandidateProfile()
    matcher = IntelligentJobMatcher(profile)
    
    # Test job that should pass
    test_job = {
        'title': 'Safety Coordinator',
        'company': 'Devon Energy',
        'location': 'Oklahoma City, OK',
        'description': 'Coordinate safety programs for drilling operations. Oil and gas experience preferred.',
        'salary_min': 65000,
        'salary_max': 85000,
        'remote_friendly': False,
        'employment_type': 'FULLTIME',
        'url': 'https://example.com'
    }
    
    print("\n🔍 Testing Acceptable Job")
    print("=" * 50)
    print(f"Job: {test_job['title']}")
    print(f"Company: {test_job['company']}")
    print(f"Salary: ${test_job['salary_max']:,}")
    print()
    
    # Calculate match score
    score, reasons = matcher.calculate_match_score(test_job)
    
    print(f"Match Score: {score:.3f}")
    print()
    print("Scoring Breakdown:")
    for reason in reasons:
        if "PENALTY" in reason or "BONUS" in reason:
            print(f"  📌 {reason}")
        else:
            print(f"  • {reason}")
    
    print()
    
    # Check if it would pass
    minimum_score = 0.5
    if score >= minimum_score:
        print(f"✅ PASSED: Job correctly accepted (score {score:.3f} >= minimum {minimum_score})")
        return True
    else:
        print(f"❌ FAILED: Good job was filtered out (score {score:.3f} < minimum {minimum_score})")
        return False

if __name__ == "__main__":
    print("🧪 Testing Overqualification Filter System")
    print("🎯 Verifying penalties are applied correctly")
    print()
    
    test1_passed = test_overqualification_penalties()
    test2_passed = test_acceptable_job()
    
    print("\n" + "=" * 50)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED - Overqualification filter working correctly!")
    else:
        print("❌ TESTS FAILED - Check penalty configuration")
    
    print("\n💡 To use the fixed system, run:")
    print("   python3 mcp_enhanced_job_system.py")
    print("   (NOT production_job_system_v2.py)")