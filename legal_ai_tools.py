"""
Legal AI Tools Information
Comprehensive information about leading AI legal tools and their capabilities
"""

LEGAL_AI_TOOLS = {
    "Spellbook": {
        "description": "Best for contract drafting and review, integrating directly into Microsoft Word to redline and suggest legal clauses.",
        "best_for": ["Contract Drafting", "Document Review", "Microsoft Word Integration"],
        "key_features": [
            "Direct Microsoft Word integration",
            "AI-powered clause suggestions",
            "Contract redlining capabilities",
            "Legal language optimization",
            "Template-based drafting"
        ],
        "pricing": "Enterprise pricing (contact for quotes)",
        "ideal_users": ["Corporate lawyers", "Contract managers", "Legal departments"],
        "strengths": ["Seamless Word integration", "Contract specialization", "User-friendly interface"],
        "limitations": ["Microsoft ecosystem dependent", "Primarily contract-focused"]
    },
    
    "Thomson Reuters CoCounsel": {
        "description": "Leading tool for legal research and case preparation, providing reliable, cited legal research and document analysis.",
        "best_for": ["Legal Research", "Case Preparation", "Document Analysis"],
        "key_features": [
            "Comprehensive legal research",
            "Cited legal authorities",
            "Document analysis and summarization",
            "Case law research",
            "Westlaw integration"
        ],
        "pricing": "Subscription-based (varies by firm size)",
        "ideal_users": ["Law firms", "Legal researchers", "Litigation attorneys"],
        "strengths": ["Reliable sources", "Comprehensive database", "Professional citations"],
        "limitations": ["Higher cost", "Requires subscription", "Learning curve"]
    },
    
    "Lexis+ AI": {
        "description": "Provides conversational AI search with real-time Shepard's validation, allowing for rapid legal research and document summarization.",
        "best_for": ["Legal Research", "Document Summarization", "Case Analysis"],
        "key_features": [
            "Conversational AI search",
            "Real-time Shepard's validation",
            "Document summarization",
            "Case law analysis",
            "Natural language queries"
        ],
        "pricing": "Premium subscription required",
        "ideal_users": ["Legal practitioners", "Law firms", "Academic institutions"],
        "strengths": ["Natural language interface", "Shepard's validation", "Comprehensive database"],
        "limitations": ["Premium pricing", "Requires LexisNexis subscription", "Complex interface"]
    },
    
    "Lex Machina": {
        "description": "Focuses on litigation analytics to predict case outcomes, analyze judicial behavior, and gain a competitive edge in litigation.",
        "best_for": ["Litigation Analytics", "Case Outcome Prediction", "Judicial Behavior Analysis"],
        "key_features": [
            "Case outcome prediction",
            "Judicial behavior analysis",
            "Litigation analytics",
            "Competitive intelligence",
            "Data-driven insights"
        ],
        "pricing": "Enterprise pricing (custom quotes)",
        "ideal_users": ["Litigation firms", "Corporate counsel", "Insurance companies"],
        "strengths": ["Predictive analytics", "Data-driven insights", "Competitive intelligence"],
        "limitations": ["Litigation-specific", "High cost", "Requires data expertise"]
    },
    
    "Clio Manage AI": {
        "description": "A comprehensive practice management tool that helps automate client intake, scheduling, and document management.",
        "best_for": ["Practice Management", "Client Intake", "Document Management"],
        "key_features": [
            "Automated client intake",
            "Smart scheduling",
            "Document management",
            "Practice analytics",
            "Client communication tools"
        ],
        "pricing": "Tiered subscription ($39-$89+ per user/month)",
        "ideal_users": ["Small firms", "Solo practitioners", "Legal departments"],
        "strengths": ["All-in-one solution", "Affordable pricing", "User-friendly"],
        "limitations": ["Not litigation-focused", "Basic AI capabilities", "Practice management focus"]
    },
    
    "Harvey AI": {
        "description": "Designed for large firm research and complex drafting, built on advanced LLMs (like GPT-5) to handle specialized tasks.",
        "best_for": ["Complex Legal Research", "Advanced Drafting", "Large Firm Operations"],
        "key_features": [
            "Advanced LLM technology",
            "Complex legal research",
            "Sophisticated drafting",
            "Large-scale operations",
            "Custom AI solutions"
        ],
        "pricing": "Enterprise pricing (custom solutions)",
        "ideal_users": ["Large law firms", "Corporate legal departments", "Government agencies"],
        "strengths": ["Advanced technology", "Customizable", "Enterprise-grade"],
        "limitations": ["High cost", "Large firms only", "Complex implementation"]
    },
    
    "Superlegal": {
        "description": "Offers AI-powered contract review with additional human attorney oversight for enhanced reliability.",
        "best_for": ["Contract Review", "Risk Assessment", "Quality Assurance"],
        "key_features": [
            "AI-powered contract review",
            "Human attorney oversight",
            "Risk assessment",
            "Quality assurance",
            "Compliance checking"
        ],
        "pricing": "Per-document pricing (varies by complexity)",
        "ideal_users": ["Corporate legal departments", "Contract managers", "Risk officers"],
        "strengths": ["Human oversight", "Quality focus", "Risk mitigation"],
        "limitations": ["Per-document cost", "Limited to contracts", "Human dependency"]
    }
}

USE_CASE_RECOMMENDATIONS = {
    "Contract Drafting": ["Spellbook", "Harvey AI"],
    "Legal Research": ["Thomson Reuters CoCounsel", "Lexis+ AI", "Harvey AI"],
    "Litigation": ["Lex Machina", "Thomson Reuters CoCounsel"],
    "Practice Management": ["Clio Manage AI"],
    "Document Review": ["Superlegal", "Thomson Reuters CoCounsel", "Spellbook"],
    "Small Firm": ["Clio Manage AI", "Spellbook"],
    "Large Firm": ["Harvey AI", "Thomson Reuters CoCounsel", "Lex Machina"],
    "Corporate Legal": ["Superlegal", "Lex Machina", "Harvey AI"]
}

def get_tool_info(tool_name: str) -> dict:
    """Get detailed information about a specific AI tool"""
    return LEGAL_AI_TOOLS.get(tool_name, {})

def get_tools_by_use_case(use_case: str) -> list:
    """Get recommended tools for a specific use case"""
    return USE_CASE_RECOMMENDATIONS.get(use_case, [])

def get_all_tools() -> dict:
    """Get all available AI tools information"""
    return LEGAL_AI_TOOLS

def get_all_use_cases() -> list:
    """Get all available use cases"""
    return list(USE_CASE_RECOMMENDATIONS.keys())

def compare_tools(tool_names: list) -> dict:
    """Compare multiple AI tools side by side"""
    comparison = {}
    for tool_name in tool_names:
        if tool_name in LEGAL_AI_TOOLS:
            comparison[tool_name] = {
                "best_for": LEGAL_AI_TOOLS[tool_name]["best_for"],
                "pricing": LEGAL_AI_TOOLS[tool_name]["pricing"],
                "ideal_users": LEGAL_AI_TOOLS[tool_name]["ideal_users"],
                "strengths": LEGAL_AI_TOOLS[tool_name]["strengths"]
            }
    return comparison

def recommend_tools(budget: str, firm_size: str, practice_area: str) -> list:
    """Get AI tool recommendations based on user needs"""
    recommendations = []
    
    # Budget-based filtering
    if budget == "low":
        affordable_tools = ["Clio Manage AI", "Spellbook"]
    elif budget == "medium":
        affordable_tools = ["Clio Manage AI", "Spellbook", "Superlegal", "Lexis+ AI"]
    else:  # high budget
        affordable_tools = list(LEGAL_AI_TOOLS.keys())
    
    # Firm size filtering
    if firm_size == "small":
        size_appropriate = ["Clio Manage AI", "Spellbook", "Superlegal"]
    elif firm_size == "medium":
        size_appropriate = ["Clio Manage AI", "Spellbook", "Superlegal", "Lexis+ AI", "Thomson Reuters CoCounsel"]
    else:  # large
        size_appropriate = ["Harvey AI", "Lex Machina", "Thomson Reuters CoCounsel", "Lexis+ AI"]
    
    # Practice area filtering
    practice_tools = get_tools_by_use_case(practice_area) if practice_area in USE_CASE_RECOMMENDATIONS else []
    
    # Find intersection
    if practice_tools:
        recommendations = [tool for tool in practice_tools if tool in affordable_tools and tool in size_appropriate]
    else:
        recommendations = [tool for tool in affordable_tools if tool in size_appropriate]
    
    return recommendations[:3]  # Return top 3 recommendations

if __name__ == "__main__":
    # Test the module
    print("Legal AI Tools Information Module")
    print("=" * 50)
    
    # Test tool info
    print("\nSpellbook Info:")
    spellbook_info = get_tool_info("Spellbook")
    for key, value in spellbook_info.items():
        print(f"  {key}: {value}")
    
    # Test use case recommendations
    print("\nContract Drafting Recommendations:")
    contract_tools = get_tools_by_use_case("Contract Drafting")
    print(f"  Recommended tools: {contract_tools}")
    
    # Test recommendations
    print("\nRecommendations for Small Firm, Low Budget, Contract Drafting:")
    recs = recommend_tools("low", "small", "Contract Drafting")
    print(f"  Top recommendations: {recs}")
