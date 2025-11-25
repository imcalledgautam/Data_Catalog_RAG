"""
FastAPI REST Backend for Bank Data Catalog
Provides REST endpoints for the frontend to interact with Neo4j
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Bank Data Catalog API",
    description="REST API for Text-to-Cypher Bank Data Catalog",
    version="1.0.0"
)

# CORS Configuration - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Neo4j connection
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client (v1.0+ API)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Pydantic Models for Request/Response
class QuestionRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    explanation: str
    cypher_query: str
    sql_query: Optional[str] = None
    results: List[Dict[str, Any]]
    summary: Optional[str] = None
    timestamp: str

class CypherRequest(BaseModel):
    cypher: str

class TableInfo(BaseModel):
    name: str
    description: str
    columns: List[Dict[str, Any]]

class LineageNode(BaseModel):
    id: str
    label: str
    type: str

class LineageEdge(BaseModel):
    source: str
    target: str
    type: str

class LineageResponse(BaseModel):
    nodes: List[LineageNode]
    edges: List[LineageEdge]


# Neo4j Driver Helper
def get_neo4j_driver():
    """Create Neo4j driver instance"""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def generate_cypher_from_question(question: str) -> tuple:
    """
    Generate Cypher query from natural language question using OpenAI
    Returns: (explanation, cypher_query)
    """
    driver = get_neo4j_driver()

    try:
        # Get schema context
        with driver.session() as session:
            schema_query = """
            MATCH (t:Table)-[:HAS_COLUMN]->(c:Column)
            RETURN t.name as table, collect({name: c.name, type: c.data_type}) as columns
            LIMIT 20
            """
            schema_result = session.run(schema_query)
            schema_context = [dict(record) for record in schema_result]

        # Build prompt for OpenAI
        prompt = f"""You are a Cypher query expert for Neo4j databases.

Schema Context:
{schema_context}

User Question: {question}

Generate a valid Cypher query to answer this question. The database contains:
- Data nodes: Client, Bank_account, Card_detail, Card_transaction, Loan_record, Employee, Branche, Customer_support, Online_transaction
- Metadata nodes: Table, Column, CDE, Region
- Relationships: HAS_ACCOUNT, HAS_CARD, HAS_LOAN, HAS_TRANSACTION, HAS_COLUMN, IS_CDE_FOR, BELONGS_TO_REGION, LOADS_INTO, JOINS

Provide:
1. A brief explanation of what the query does
2. The Cypher query itself

Format your response as:
EXPLANATION: <explanation>
CYPHER: <query>
"""

        # Call OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Neo4j Cypher expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        content = response.choices[0].message.content

        # Parse response
        explanation = ""
        cypher_query = ""

        if "EXPLANATION:" in content and "CYPHER:" in content:
            parts = content.split("CYPHER:")
            explanation = parts[0].replace("EXPLANATION:", "").strip()
            cypher_query = parts[1].strip()
        else:
            # Fallback parsing
            lines = content.split('\n')
            cypher_lines = []
            in_cypher = False

            for line in lines:
                if line.strip().upper().startswith(('MATCH', 'RETURN', 'WHERE', 'WITH', 'CREATE', 'MERGE')):
                    in_cypher = True
                if in_cypher:
                    cypher_lines.append(line)

            cypher_query = '\n'.join(cypher_lines).strip()
            explanation = "Generated Cypher query for your question."

        return explanation, cypher_query

    finally:
        driver.close()


def execute_cypher_query(cypher: str) -> List[Dict[str, Any]]:
    """Execute Cypher query and return results"""
    driver = get_neo4j_driver()

    try:
        with driver.session() as session:
            result = session.run(cypher)
            records = []
            for record in result:
                records.append(dict(record))
            return records
    finally:
        driver.close()


def generate_summary(question: str, results: List[Dict], cypher: str) -> str:
    """Generate AI summary of query results"""
    if not results:
        return "No results found for your query."

    # Limit results for summary (first 10 records)
    sample_results = results[:10]

    prompt = f"""Based on the following query results, provide a concise business summary.

User Question: {question}
Cypher Query: {cypher}
Results (sample): {sample_results}
Total Records: {len(results)}

Provide a clear, business-friendly summary of what the data shows."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst providing business insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary generation failed: {str(e)}"


def generate_sql_from_cypher(cypher_query: str, question: str) -> str:
    """
    Convert Cypher query to equivalent SQL query using OpenAI
    Helps users understand the query in familiar SQL syntax
    """
    prompt = f"""You are a database expert. Convert this Neo4j Cypher query to an equivalent SQL query.

Original Question: {question}

Cypher Query:
{cypher_query}

Database Schema (assume relational):
- clients (client_id, first_name, last_name, email_address, phone_number, date_of_birth, address, city, state, zip_code, country, account_opening_date)
- bank_accounts (account_id, client_id, account_no, balance_amount, account_category, account_opening_date, account_status)
- account_types (account_category, min_balance_req, interest_rate, monthly_fee)
- card_details (card_id, client_id, card_number, card_type, card_status, card_issue_date, card_expiry_date)
- card_transactions (transaction_id, card_id, merchant_name, transaction_amount, transaction_date, transaction_status)
- loan_records (loan_id, client_id, loan_amount, interest_rate, loan_status, loan_start_date, loan_end_date, monthly_payment)
- employees (employee_id, emp_first_name, emp_last_name, emp_role, emp_salary, emp_hire_date, branch_id)
- branches (branch_id, branch_name, branch_address, branch_city, branch_state, branch_zip, branch_phone)
- customer_support (ticket_id, client_id, issue_category, issue_description, ticket_status, ticket_created_date, ticket_resolved_date)
- online_transactions (online_txn_id, account_id, txn_amount, txn_date, txn_status, payment_method)

Relationships (for joins):
- clients.client_id → bank_accounts.client_id
- clients.client_id → card_details.client_id
- clients.client_id → loan_records.client_id
- card_details.card_id → card_transactions.card_id
- employees.branch_id → branches.branch_id
- clients.client_id → customer_support.client_id
- bank_accounts.account_id → online_transactions.account_id
- bank_accounts.account_category → account_types.account_category

Convert the Cypher query to a valid SQL query (PostgreSQL/MySQL compatible).
Return ONLY the SQL query, no explanations."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a database expert converting Cypher to SQL. Return only valid SQL code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        sql_query = response.choices[0].message.content.strip()

        # Clean up the response (remove markdown code blocks if present)
        if sql_query.startswith("```sql"):
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        elif sql_query.startswith("```"):
            sql_query = sql_query.replace("```", "").strip()

        return sql_query
    except Exception as e:
        return f"-- SQL generation failed: {str(e)}"


# API ENDPOINTS

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Bank Data Catalog API",
        "version": "1.0.0"
    }


@app.post("/api/ask", response_model=QueryResponse)
async def ask_question(request: QuestionRequest):
    """
    Main endpoint: Convert natural language question to Cypher, execute, and return results
    Also generates equivalent SQL query for user understanding
    """
    try:
        # Generate Cypher from question
        explanation, cypher_query = generate_cypher_from_question(request.question)

        if not cypher_query:
            raise HTTPException(status_code=400, detail="Failed to generate Cypher query")

        # Execute query
        results = execute_cypher_query(cypher_query)

        # Generate SQL equivalent from Cypher
        sql_query = generate_sql_from_cypher(cypher_query, request.question)

        # Generate summary
        summary = generate_summary(request.question, results, cypher_query)

        return QueryResponse(
            explanation=explanation,
            cypher_query=cypher_query,
            sql_query=sql_query,
            results=results,
            summary=summary,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@app.post("/api/query/cypher")
async def run_cypher(request: CypherRequest):
    """
    Execute raw Cypher query
    """
    try:
        results = execute_cypher_query(request.cypher)
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cypher execution failed: {str(e)}")


@app.get("/api/schema/tables")
async def get_tables():
    """
    Get all tables in the metadata graph
    """
    driver = get_neo4j_driver()

    try:
        with driver.session() as session:
            query = """
            MATCH (t:Table)
            OPTIONAL MATCH (t)-[:HAS_COLUMN]->(c:Column)
            RETURN t.name as name,
                   t.description as description,
                   collect({
                       name: c.name,
                       data_type: c.data_type
                   }) as columns
            ORDER BY t.name
            """
            result = session.run(query)
            tables = [dict(record) for record in result]
            return {"tables": tables, "count": len(tables)}
    finally:
        driver.close()


@app.get("/api/schema/table/{table_name}")
async def get_table_details(table_name: str):
    """
    Get detailed information about a specific table
    """
    driver = get_neo4j_driver()

    try:
        with driver.session() as session:
            query = """
            MATCH (t:Table {name: $table_name})
            OPTIONAL MATCH (t)-[:HAS_COLUMN]->(c:Column)
            OPTIONAL MATCH (c)-[:IS_CDE_FOR]->(cde:CDE)
            OPTIONAL MATCH (t)-[:BELONGS_TO_REGION]->(r:Region)
            RETURN t.name as name,
                   t.description as description,
                   collect(DISTINCT {
                       name: c.name,
                       data_type: c.data_type,
                       is_cde: cde.name IS NOT NULL,
                       cde_name: cde.name
                   }) as columns,
                   collect(DISTINCT r.name) as regions
            """
            result = session.run(query, table_name=table_name)
            record = result.single()

            if not record:
                raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

            return dict(record)
    finally:
        driver.close()


@app.get("/api/lineage/{table_name}", response_model=LineageResponse)
async def get_lineage(table_name: str, depth: int = Query(default=2, ge=1, le=5)):
    """
    Get data lineage for a table (upstream and downstream)
    """
    driver = get_neo4j_driver()

    try:
        with driver.session() as session:
            # Get upstream and downstream tables
            query = f"""
            MATCH path = (t:Table {{name: $table_name}})-[:LOADS_INTO*1..{depth}]-(related:Table)
            RETURN t, related, relationships(path) as rels
            UNION
            MATCH path = (related:Table)-[:LOADS_INTO*1..{depth}]->(t:Table {{name: $table_name}})
            RETURN t, related, relationships(path) as rels
            """
            result = session.run(query, table_name=table_name)

            nodes = {}
            edges = []

            # Add center node
            nodes[table_name] = LineageNode(
                id=table_name,
                label=table_name,
                type="center"
            )

            for record in result:
                t_node = record['t']
                related_node = record['related']
                rels = record['rels']

                # Add related node
                related_name = related_node['name']
                if related_name not in nodes:
                    nodes[related_name] = LineageNode(
                        id=related_name,
                        label=related_name,
                        type="related"
                    )

                # Add edges
                for rel in rels:
                    source = rel.start_node['name']
                    target = rel.end_node['name']
                    edges.append(LineageEdge(
                        source=source,
                        target=target,
                        type="LOADS_INTO"
                    ))

            return LineageResponse(
                nodes=list(nodes.values()),
                edges=edges
            )
    finally:
        driver.close()


@app.get("/api/search/tables")
async def search_tables(q: str = Query(..., min_length=1)):
    """
    Search tables by name or description
    """
    driver = get_neo4j_driver()

    try:
        with driver.session() as session:
            query = """
            MATCH (t:Table)
            WHERE toLower(t.name) CONTAINS toLower($search)
               OR toLower(t.description) CONTAINS toLower($search)
            RETURN t.name as name, t.description as description
            LIMIT 20
            """
            result = session.run(query, search=q)
            tables = [dict(record) for record in result]
            return {"tables": tables, "count": len(tables)}
    finally:
        driver.close()


@app.get("/api/stats")
async def get_stats():
    """
    Get database statistics
    """
    driver = get_neo4j_driver()

    try:
        with driver.session() as session:
            # Count various node types
            queries = {
                "tables": "MATCH (t:Table) RETURN count(t) as count",
                "columns": "MATCH (c:Column) RETURN count(c) as count",
                "clients": "MATCH (c:Client) RETURN count(c) as count",
                "accounts": "MATCH (a:Bank_account) RETURN count(a) as count",
                "transactions": "MATCH (t:Card_transaction) RETURN count(t) as count",
                "loans": "MATCH (l:Loan_record) RETURN count(l) as count",
            }

            stats = {}
            for key, query in queries.items():
                result = session.run(query)
                record = result.single()
                stats[key] = record['count'] if record else 0

            return {"stats": stats}
    finally:
        driver.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
