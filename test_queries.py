from chat import LegalAssistant

# Initialize the legal assistant
assistant = LegalAssistant()

questions = [
    "What is a contract?",
    "How does child custody work?",
    "What is a will?",
    "What is a tort?",
    "What is intellectual property?"
]

print("🤖 AI Legal Assistant - Multiple Questions Test")
print("=" * 60)

for q in questions:
    print(f"\n📝 Question: {q}")
    print("🤖 Answer:")
    print(assistant.ask_legal(q))
    print("-" * 50)

print("\n✅ All questions completed!")