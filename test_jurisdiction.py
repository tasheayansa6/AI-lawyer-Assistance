"""
Test Jurisdiction Functionality
Tests the ask_legal method with different jurisdictions
"""

from chat import LegalAssistant

def test_jurisdictions():
    """Test legal assistant with different jurisdictions"""
    assistant = LegalAssistant()
    
    test_question = "What is a power of attorney?"
    jurisdictions = ["US", "UK", "India", "Canada", "Australia", "Ethiopia"]
    
    print("🌍 Testing Jurisdiction Functionality")
    print("=" * 60)
    
    for jurisdiction in jurisdictions:
        print(f"\n📍 Testing {jurisdiction} Law:")
        print("-" * 30)
        
        try:
            response = assistant.ask_legal(test_question, jurisdiction)
            print(f"✅ {jurisdiction} Response Generated")
            print(f"📝 Preview: {response[:200]}...")
            print()
        except Exception as e:
            print(f"❌ Error with {jurisdiction}: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Jurisdiction Testing Complete!")

if __name__ == "__main__":
    test_jurisdictions()
