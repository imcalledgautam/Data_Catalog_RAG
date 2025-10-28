"""
Test script to run example queries against the Neo4j database with mock bank data.
This script demonstrates the LLM agent's ability to generate and execute Cypher queries.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neo4j_setup import Neo4jSetup
from src.agent import generate_lineage_response


def run_test_query(setup, question, query_num):
    """Run a single test query and display results."""
    print("="*80)
    print(f"QUERY {query_num}: {question}")
    print("="*80)
    print()
    
    try:
        # generate_lineage_response returns a tuple: (explanation, cypher)
        explanation, cypher = generate_lineage_response(question)
        
        print(f"[Generated Cypher Query]:")
        print(cypher if cypher else explanation)
        print()
        
        # Execute the generated query
        if cypher and cypher.strip() and not cypher.startswith("Error") and not cypher.startswith("OPENAI"):
            with setup.driver.session() as session:
                result = session.run(cypher)
                records = list(result)
                
                print(f"[Query Results]: {len(records)} record(s) found")
                print()
                
                # Display first 5 results
                for i, record in enumerate(records[:5], 1):
                    print(f"Result {i}:")
                    for key in record.keys():
                        value = record[key]
                        # Truncate long strings
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:97] + "..."
                        print(f"  {key}: {value}")
                    print()
                
                if len(records) > 5:
                    print(f"... and {len(records) - 5} more results")
                    print()
        else:
            print(f"[Explanation]: {explanation}")
            print()
            
    except Exception as e:
        print(f"[Error]: {e}")
        import traceback
        traceback.print_exc()
        print()
    
    print("="*80)
    print()


def main():
    print("="*80)
    print("TESTING LLM TEXT-TO-CYPHER WITH MOCK BANK DATA")
    print("="*80)
    print()
    
    setup = Neo4jSetup()
    
    # Example queries to test
    test_queries = [
        "Show all clients who have a savings account.",
        "List all transactions above $5000 for any card.",
        "Find all employees working in branches located in Mumbai.",
        "Which clients have active loans?",
        "Show all card transactions for blocked cards.",
        "List the top 5 clients by total account balance.",
        "Find all clients with both a checking account and a credit card.",
        "Show all customer support tickets that are still open.",
    ]
    
    print(f"Running {len(test_queries)} test queries...\n")
    
    for i, question in enumerate(test_queries, 1):
        run_test_query(setup, question, i)
    
    print()
    print("="*80)
    print("TEST EXECUTION COMPLETED")
    print("="*80)
    
    setup.close()


if __name__ == "__main__":
    main()
