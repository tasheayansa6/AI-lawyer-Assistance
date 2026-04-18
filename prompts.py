"""
Legal Prompt Templates
Professional prompt templates for different types of legal queries
"""

TEMPLATES = {
    "general": "Answer this legal question: {query}",
    "term": "Define and explain this legal term in simple language: {query}",
    "process": "Explain the step-by-step legal process for: {query}",
    "rights": "What are the legal rights regarding: {query}",
    "deadline": "What are the typical deadlines or statutes of limitations for: {query}",
    "requirements": "What are the legal requirements for: {query}",
    "consequences": "What are the legal consequences of: {query}",
    "documentation": "What documentation is needed for: {query}",
    "procedure": "What is the legal procedure for: {query}",
    "costs": "What are the typical costs and fees associated with: {query}",
    "timeline": "What is the typical timeline for: {query}",
    "evidence": "What evidence is needed for: {query}",
    "defenses": "What are the common legal defenses for: {query}",
    "settlement": "How are settlements typically handled for: {query}",
    "appeal": "What is the appeals process for: {query}"
}

def get_prompt(template_type: str, query: str) -> str:
    """
    Get formatted prompt based on template type
    
    Args:
        template_type (str): Type of template to use
        query (str): The user's query
        
    Returns:
        str: Formatted prompt
    """
    if template_type not in TEMPLATES:
        return TEMPLATES["general"].format(query=query)
    
    return TEMPLATES[template_type].format(query=query)

def get_template_descriptions() -> dict:
    """
    Get descriptions for each template type
    
    Returns:
        dict: Template descriptions
    """
    return {
        "general": "General legal questions",
        "term": "Explain legal terms",
        "process": "Step-by-step processes",
        "rights": "Legal rights information",
        "deadline": "Statutes of limitations",
        "requirements": "Legal requirements",
        "consequences": "Legal consequences",
        "documentation": "Required documents",
        "procedure": "Legal procedures",
        "costs": "Legal costs and fees",
        "timeline": "Process timelines",
        "evidence": "Evidence requirements",
        "defenses": "Legal defenses",
        "settlement": "Settlement processes",
        "appeal": "Appeals processes"
    }

def list_templates():
    """List all available template types"""
    return list(TEMPLATES.keys())

# Example usage
if __name__ == "__main__":
    # Test templates
    test_query = "power of attorney"
    
    print("Available Templates:")
    for template_type, description in get_template_descriptions().items():
        print(f"  {template_type}: {description}")
    
    print("\nTemplate Examples:")
    for template_type in list_templates()[:3]:  # Show first 3 examples
        prompt = get_prompt(template_type, test_query)
        print(f"\n{template_type.upper()}:")
        print(f"  {prompt}")
