"""
Test Response Length Control Functionality
Tests ask_legal method with different max_tokens values
"""

from chat import LegalAssistant

def test_response_length():
    """Test legal assistant with different response lengths"""
    assistant = LegalAssistant()
    
    test_question = "What is a contract?"
    max_tokens_values = [100, 300, 500, 800, 1000]
    
    print("📏 Testing Response Length Control")
    print("=" * 60)
    
    for max_tokens in max_tokens_values:
        print(f"\n🎯 Testing with {max_tokens} max tokens:")
        print("-" * 40)
        
        try:
            response = assistant.ask_legal(test_question, "US", max_tokens)
            word_count = len(response.split())
            print(f"✅ Response Generated")
            print(f"📊 Word Count: {word_count}")
            print(f"📝 Preview: {response[:150]}...")
            print()
        except Exception as e:
            print(f"❌ Error with {max_tokens} tokens: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Response Length Testing Complete!")

if __name__ == "__main__":
    test_response_length()
