import os
import requests
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


CYPHER_GENERATION_TEMPLATE = """
You are an expert in generating Cypher queries for Neo4j graph databases containing bank data and metadata.

Task: Convert the user's natural language question into a precise Cypher query.

Graph Schema:
{schema}

Important Rules:
1. The database contains BOTH actual data nodes (Client, Bank_account, etc.) AND metadata nodes (Table, Column)
2. For questions about actual data (clients, accounts, transactions), query the data nodes directly
3. For questions about schema/lineage, query the metadata nodes (Table, Column)
4. Data nodes are connected via typed relationships (HAS_ACCOUNT, HAS_CARD, HAS_LOAN, TRANSACTION_FOR, etc.)
5. Use property matching with EXACT case (e.g., card_status='Blocked', loan_status='Active', account_category='Savings')
6. Return relevant properties from the data nodes
7. Use aggregation functions (COUNT, SUM, AVG) where appropriate
8. For lineage queries, use LOADS_INTO and JOINS relationships between Table nodes

Question: {question}

Generate only the Cypher query without any explanation or markdown:
"""


def generate_lineage_response(question: str) -> tuple:
    # If the OPENAI_API_KEY is not set, fail gracefully
    if not OPENAI_API_KEY:
        return ("OPENAI_API_KEY not set in environment. Cannot generate Cypher via LLM.", "")

    # Provide a comprehensive schema hint including both metadata and data nodes
    schema_hint = (
        "Nodes (Data): Client{client_id,first_name,last_name,email_address}, "
        "Bank_account{account_id,account_no,balance_amount,account_category,client_id}, "
        "Account_type{account_category,min_balance_req,interest_rate}, "
        "Card_detail{card_id,card_number,card_type,card_status,client_id}, "
        "Card_transaction{transaction_id,card_id,merchant_name,transaction_amount,transaction_type,transaction_status}, "
        "Loan_record{loan_id,client_id,loan_amount,loan_status,interest_rate}, "
        "Employee{employee_id,emp_first_name,emp_last_name,emp_role,branch_id}, "
        "Branche{branch_id,branch_name,branch_city,branch_state}, "
        "Customer_support{ticket_id,client_id,issue_category,ticket_status}, "
        "Online_transaction{online_txn_id,account_id,txn_amount,payment_method}. "
        "Nodes (Metadata): Table{name,description}, Column{name}. "
        "Relationships (Data): HAS_ACCOUNT (Client->Bank_account), HAS_CARD (Client->Card_detail), "
        "HAS_LOAN (Client->Loan_record), HAS_TRANSACTION (Card_detail/Bank_account->Transaction), "
        "APPLIES_TO (Account_type->Bank_account), HAS_EMPLOYEE (Branche->Employee). "
        "Relationships (Metadata): HAS_COLUMN (Table->Column), LOADS_INTO{lineage_type}, JOINS{join_key}. "
        "IMPORTANT: Property values are case-sensitive. Use 'Savings'/'Current'/'Fixed' for account_category, "
        "'Active'/'Blocked' for card_status, 'Active'/'Paid'/'Defaulted' for loan_status, 'Open'/'Closed' for ticket_status."
    )

    prompt = CYPHER_GENERATION_TEMPLATE.format(schema=schema_hint, question=question)

    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 800
        }

        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=60)
        if r.status_code != 200:
            return (f"OpenAI request failed: {r.status_code} {r.text}", "")
        resp = r.json()
        try:
            generated_cypher = resp["choices"][0]["message"]["content"].strip()
        except Exception:
            generated_cypher = str(resp)

    except Exception as e:
        return (f"OpenAI request failed: {e}", "")

    # Execute the generated Cypher against Neo4j
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run(generated_cypher)
            records = [record.data() for record in result]
        driver.close()

        explanation = f"Executed Cypher; returned {len(records)} record(s). Sample: {records[:3]}"
        return (explanation, generated_cypher)

    except Exception as e:
        return (f"Error executing Cypher on Neo4j: {e}", generated_cypher)


if __name__ == "__main__":
    test_question = "Show lineage for the DEPOSIT_SUMMARY table."
    explanation, cypher = generate_lineage_response(test_question)
    print(f"\nQuestion: {test_question}")
    print(f"\nGenerated Cypher:\n{cypher}")
    print(f"\nExplanation:\n{explanation}")
