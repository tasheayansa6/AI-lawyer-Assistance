"""
Test Phase 2 Features
Comprehensive testing for all new Phase 2 functionality
"""

from chat import LegalAssistant
from prompts import get_prompt, get_template_descriptions, list_templates

def test_phase2_features():
    """Test all Phase 2 features comprehensively"""
    assistant = LegalAssistant()
    
    print("Phase 2 Features Comprehensive Test")
    print("=" * 60)
    
    # Test 1: Legal Term Explainer
    print("\n1. Testing Legal Term Explainer")
    print("-" * 40)
    try:
        term_explanation = assistant.explain_term("Power of Attorney", "US", 300)
        print("Legal Term Explainer: PASS")
        print(f"Preview: {term_explanation[:150]}...")
    except Exception as e:
        print(f"Legal Term Explainer: FAIL - {e}")
    
    # Test 2: Legal Process Guide
    print("\n2. Testing Legal Process Guide")
    print("-" * 40)
    try:
        process_guide = assistant.legal_process("Filing for divorce", "US", 500)
        print("Legal Process Guide: PASS")
        print(f"Preview: {process_guide[:150]}...")
    except Exception as e:
        print(f"Legal Process Guide: FAIL - {e}")
    
    # Test 3: Prompt Templates
    print("\n3. Testing Prompt Templates")
    print("-" * 40)
    try:
        # Test template system
        templates = list_templates()
        descriptions = get_template_descriptions()
        
        print(f"Available Templates: {len(templates)}")
        print(f"Template Descriptions: {len(descriptions)}")
        
        # Test a few templates
        test_query = "contract dispute"
        for template_type in ["general", "term", "rights"]:
            formatted_prompt = get_prompt(template_type, test_query)
            print(f"Template '{template_type}': {formatted_prompt}")
        
        print("Prompt Templates: PASS")
    except Exception as e:
        print(f"Prompt Templates: FAIL - {e}")
    
    # Test 4: Enhanced ask_legal with max_tokens
    print("\n4. Testing Enhanced ask_legal with max_tokens")
    print("-" * 40)
    try:
        # Test different token lengths
        for tokens in [200, 500, 800]:
            response = assistant.ask_legal("What is a contract?", "US", tokens)
            word_count = len(response.split())
            print(f"Tokens {tokens}: {word_count} words - PASS")
    except Exception as e:
        print(f"Enhanced ask_legal: FAIL - {e}")
    
    # Test 5: Ethiopia Jurisdiction
    print("\n5. Testing Ethiopia Jurisdiction")
    print("-" * 40)
    try:
        ethiopia_response = assistant.ask_legal("What is a contract?", "Ethiopia", 300)
        print("Ethiopia Jurisdiction: PASS")
        print(f"Preview: {ethiopia_response[:150]}...")
    except Exception as e:
        print(f"Ethiopia Jurisdiction: FAIL - {e}")
    
    print("\n" + "=" * 60)
    print("Phase 2 Features Testing Complete!")

if __name__ == "__main__":
    test_phase2_features()
