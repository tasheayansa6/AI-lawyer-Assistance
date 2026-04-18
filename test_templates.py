"""
Test All Templates - Day 17
Comprehensive testing of all 15 prompt templates with 5 queries each
"""

from chat import LegalAssistant
from prompts import get_prompt, get_template_descriptions, list_templates
import time
import json
from datetime import datetime

# Test queries for each template type
TEMPLATE_TEST_QUERIES = {
    "general": [
        "What are the essential elements of a valid contract?",
        "How does bankruptcy affect personal assets?",
        "What is the difference between civil and criminal law?",
        "Can I sue for emotional distress?",
        "What are the requirements for a power of attorney?"
    ],
    
    "term": [
        "Habeas Corpus",
        "Statute of Limitations",
        "Due Process",
        "Consideration in contract law",
        "Tort law"
    ],
    
    "process": [
        "Filing for divorce",
        "Starting a small business",
        "Applying for a patent",
        "Filing a lawsuit",
        "Creating a will"
    ],
    
    "rights": [
        "Employee privacy in the workplace",
        "Tenant rights against eviction",
        "Consumer protection for defective products",
        "Freedom of speech limitations",
        "Patient rights in healthcare"
    ],
    
    "deadlines": [
        "Personal injury claims",
        "Contract disputes",
        "Property tax appeals",
        "Worker's compensation claims",
        "Credit card debt collection"
    ],
    
    "requirements": [
        "Starting a nonprofit organization",
        "Getting married legally",
        "Adopting a child",
        "Obtaining a business license",
        "Applying for US citizenship"
    ],
    
    "consequences": [
        "Breach of contract",
        "Driving under the influence",
        "Tax evasion",
        "Copyright infringement",
        "Violating a restraining order"
    ],
    
    "documentation": [
        "Real estate transactions",
        "Employment agreements",
        "Loan applications",
        "Immigration proceedings",
        "Medical malpractice claims"
    ],
    
    "procedures": [
        "Small claims court",
        "Jury duty selection",
        "Property deed transfer",
        "Name change process",
        "Expungement of criminal records"
    ],
    
    "costs": [
        "Hiring a lawyer for divorce",
        "Filing a patent application",
        "Starting a lawsuit",
        "Real estate closing costs",
        "Bankruptcy attorney fees"
    ],
    
    "timelines": [
        "Divorce proceedings",
        "Personal injury lawsuit",
        "Home buying process",
        "Immigration visa processing",
        "Estate probate"
    ],
    
    "evidence": [
        "Car accident claims",
        "Medical malpractice cases",
        "Contract breach disputes",
        "Workplace harassment cases",
        "Intellectual property theft"
    ],
    
    "defenses": [
        "Self-defense claims",
        "Contract disputes",
        "Criminal charges",
        "Product liability lawsuits",
        "Debt collection defense"
    ],
    
    "settlements": [
        "Personal injury claims",
        "Contract disputes",
        "Employment discrimination",
        "Medical malpractice",
        "Insurance claim disputes"
    ],
    
    "appeals": [
        "Criminal convictions",
        "Civil court decisions",
        "Family court rulings",
        "Immigration denials",
        "Tax assessment disputes"
    ]
}

def test_all_templates():
    """Test all 15 templates with 5 queries each"""
    assistant = LegalAssistant()
    
    print("Comprehensive Template Testing - Day 17")
    print("=" * 80)
    print(f"Testing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Templates: {len(list_templates())}")
    print(f"Total Test Queries: {len(TEMPLATE_TEST_QUERIES) * 5}")
    print("=" * 80)
    
    results = {}
    total_tests = 0
    successful_tests = 0
    failed_tests = 0
    
    for template_type in list_templates():
        print(f"\n{'='*20} Testing {template_type.upper()} Template {'='*20}")
        
        template_results = []
        queries = TEMPLATE_TEST_QUERIES.get(template_type, [])
        
        if not queries:
            print(f"Warning: No test queries found for {template_type}")
            continue
        
        for i, query in enumerate(queries, 1):
            print(f"\nTest {i}/5: {query}")
            print("-" * 50)
            
            try:
                # Format the prompt using the template
                formatted_prompt = get_prompt(template_type, query)
                print(f"Formatted Prompt: {formatted_prompt}")
                
                # Get response from AI
                start_time = time.time()
                response = assistant.ask_legal(formatted_prompt, "US", 300)
                end_time = time.time()
                
                # Calculate response metrics
                response_time = end_time - start_time
                word_count = len(response.split())
                
                test_result = {
                    "query": query,
                    "formatted_prompt": formatted_prompt,
                    "response": response,
                    "response_time": response_time,
                    "word_count": word_count,
                    "success": True,
                    "error": None
                }
                
                template_results.append(test_result)
                successful_tests += 1
                
                print(f"Response Time: {response_time:.2f} seconds")
                print(f"Word Count: {word_count}")
                print(f"Response Preview: {response[:100]}...")
                print("Status: SUCCESS")
                
            except Exception as e:
                print(f"Status: FAILED - {str(e)}")
                
                test_result = {
                    "query": query,
                    "formatted_prompt": formatted_prompt if 'formatted_prompt' in locals() else None,
                    "response": None,
                    "response_time": None,
                    "word_count": None,
                    "success": False,
                    "error": str(e)
                }
                
                template_results.append(test_result)
                failed_tests += 1
            
            total_tests += 1
            
            # Small delay between requests
            time.sleep(1)
        
        results[template_type] = {
            "template_type": template_type,
            "description": get_template_descriptions().get(template_type, "No description"),
            "total_tests": len(template_results),
            "successful_tests": len([r for r in template_results if r["success"]]),
            "failed_tests": len([r for r in template_results if not r["success"]]),
            "average_response_time": sum(r["response_time"] for r in template_results if r["response_time"]) / len([r for r in template_results if r["response_time"]]) if any(r["response_time"] for r in template_results) else 0,
            "average_word_count": sum(r["word_count"] for r in template_results if r["word_count"]) / len([r for r in template_results if r["word_count"]]) if any(r["word_count"] for r in template_results) else 0,
            "test_results": template_results
        }
        
        # Template summary
        template_summary = results[template_type]
        print(f"\nTemplate Summary:")
        print(f"Total Tests: {template_summary['total_tests']}")
        print(f"Successful: {template_summary['successful_tests']}")
        print(f"Failed: {template_summary['failed_tests']}")
        print(f"Success Rate: {(template_summary['successful_tests']/template_summary['total_tests'])*100:.1f}%")
        if template_summary['average_response_time'] > 0:
            print(f"Avg Response Time: {template_summary['average_response_time']:.2f} seconds")
        if template_summary['average_word_count'] > 0:
            print(f"Avg Word Count: {template_summary['average_word_count']:.0f} words")
    
    # Overall summary
    print(f"\n{'='*80}")
    print("OVERALL TESTING SUMMARY")
    print(f"{'='*80}")
    print(f"Total Templates Tested: {len(results)}")
    print(f"Total Tests Run: {total_tests}")
    print(f"Successful Tests: {successful_tests}")
    print(f"Failed Tests: {failed_tests}")
    print(f"Overall Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # Calculate overall averages
    all_successful_results = []
    for template_data in results.values():
        all_successful_results.extend([r for r in template_data["test_results"] if r["success"]])
    
    if all_successful_results:
        overall_avg_time = sum(r["response_time"] for r in all_successful_results) / len(all_successful_results)
        overall_avg_words = sum(r["word_count"] for r in all_successful_results) / len(all_successful_results)
        print(f"Overall Average Response Time: {overall_avg_time:.2f} seconds")
        print(f"Overall Average Word Count: {overall_avg_words:.0f} words")
    
    # Save results to file
    save_test_results(results)
    
    return results

def save_test_results(results):
    """Save test results to JSON file"""
    try:
        output_file = f"template_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error saving results: {e}")

def analyze_template_performance(results):
    """Analyze and report on template performance"""
    print(f"\n{'='*80}")
    print("TEMPLATE PERFORMANCE ANALYSIS")
    print(f"{'='*80}")
    
    # Sort templates by success rate
    templates_by_success = sorted(
        results.items(),
        key=lambda x: (x[1]["successful_tests"] / x[1]["total_tests"]) if x[1]["total_tests"] > 0 else 0,
        reverse=True
    )
    
    print("\nTemplates ranked by success rate:")
    for i, (template_name, data) in enumerate(templates_by_success, 1):
        success_rate = (data["successful_tests"] / data["total_tests"]) * 100 if data["total_tests"] > 0 else 0
        print(f"{i}. {template_name}: {success_rate:.1f}% success rate")
    
    # Sort templates by average response time
    templates_by_speed = sorted(
        [(name, data) for name, data in results.items() if data["average_response_time"] > 0],
        key=lambda x: x[1]["average_response_time"]
    )
    
    print("\nTemplates ranked by response speed:")
    for i, (template_name, data) in enumerate(templates_by_speed, 1):
        print(f"{i}. {template_name}: {data['average_response_time']:.2f} seconds avg")
    
    # Sort templates by response length
    templates_by_length = sorted(
        [(name, data) for name, data in results.items() if data["average_word_count"] > 0],
        key=lambda x: x[1]["average_word_count"],
        reverse=True
    )
    
    print("\nTemplates ranked by response length:")
    for i, (template_name, data) in enumerate(templates_by_length, 1):
        print(f"{i}. {template_name}: {data['average_word_count']:.0f} words avg")

if __name__ == "__main__":
    # Run comprehensive template testing
    results = test_all_templates()
    
    # Analyze performance
    analyze_template_performance(results)
    
    print(f"\n{'='*80}")
    print("TEMPLATE TESTING COMPLETED")
    print(f"{'='*80}")
    print("Check the generated JSON file for detailed results.")
