# Cypher to SQL Conversion Guide

## Overview

You asked about converting Cypher queries to SQL. Here are three approaches:

## Option 1: Dual Database Support (Recommended)

Modify the backend to support both Neo4j (graph) and SQL databases side-by-side.

### Implementation Steps:

1. **Add SQL Database Connection**:
```python
# In backend_api.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add to config
SQL_DATABASE_URL = "postgresql://user:password@localhost/bankdb"
engine = create_engine(SQL_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

2. **Create Dual Query Endpoint**:
```python
@app.post("/api/ask-dual")
async def ask_question_dual(request: QuestionRequest):
    """
    Process question with both Cypher and SQL
    """
    # Generate Cypher query
    cypher_explanation, cypher_query = generate_cypher_from_question(request.question)
    cypher_results = execute_cypher_query(cypher_query)

    # Generate SQL query
    sql_query = generate_sql_from_question(request.question)
    sql_results = execute_sql_query(sql_query)

    return {
        "cypher": {
            "query": cypher_query,
            "results": cypher_results
        },
        "sql": {
            "query": sql_query,
            "results": sql_results
        }
    }
```

3. **SQL Query Generation**:
```python
def generate_sql_from_question(question: str) -> str:
    """Generate SQL query from natural language"""

    # Get database schema
    schema = get_sql_schema()

    prompt = f"""You are a SQL expert for PostgreSQL/MySQL databases.

Database Schema:
{schema}

User Question: {question}

Generate a valid SQL query to answer this question.

Tables available:
- clients (client_id, first_name, last_name, email_address, etc.)
- bank_accounts (account_id, client_id, account_no, balance_amount)
- card_transactions (transaction_id, card_id, merchant_name, transaction_amount)
- loans (loan_id, client_id, loan_amount, loan_status)

Format: Return only the SQL query.
"""

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a SQL expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()
```

## Option 2: Cypher-to-SQL Translation

Programmatically convert Cypher queries to SQL equivalents.

### Conversion Mapping:

```python
def cypher_to_sql(cypher_query: str) -> str:
    """
    Convert Cypher query patterns to SQL

    Example conversions:

    Cypher: MATCH (c:Client) RETURN c.name
    SQL:    SELECT name FROM clients

    Cypher: MATCH (c:Client)-[:HAS_ACCOUNT]->(a:Bank_account)
            RETURN c.name, a.balance
    SQL:    SELECT c.name, a.balance_amount
            FROM clients c
            JOIN bank_accounts a ON c.client_id = a.client_id

    Cypher: MATCH (c:Client) WHERE c.age > 30 RETURN c
    SQL:    SELECT * FROM clients WHERE age > 30
    """

    # This is complex - requires a full parser
    # Libraries: neo4j-to-sql, cypher-parser

    import re

    # Simple pattern matching (basic cases only)
    patterns = {
        r'MATCH \(c:Client\)': 'SELECT * FROM clients',
        r'RETURN c\.(\w+)': r'SELECT \1 FROM clients',
        # Add more patterns...
    }

    sql_query = cypher_query
    for cypher_pattern, sql_replacement in patterns.items():
        sql_query = re.sub(cypher_pattern, sql_replacement, sql_query, flags=re.IGNORECASE)

    return sql_query
```

### Limitations:
- Graph relationships don't map 1:1 to SQL JOINs
- Complex patterns (variable-length paths) are hard to convert
- Performance characteristics differ significantly
- Not recommended for production

## Option 3: Display-Only SQL Generation

Generate SQL for display purposes (not execution).

### Use Case:
Show users both Cypher and SQL versions side-by-side for learning/comparison.

### Implementation:

```python
@app.post("/api/explain-sql")
async def explain_as_sql(request: CypherRequest):
    """
    Convert Cypher to equivalent SQL for display
    """

    prompt = f"""Given this Neo4j Cypher query:

{request.cypher}

Generate an equivalent SQL query that would return similar results from a relational database.

Assume these tables exist:
- clients (client_id, first_name, last_name, email, phone, etc.)
- bank_accounts (account_id, client_id, account_no, balance_amount, account_category)
- card_details (card_id, client_id, card_number, card_type)
- card_transactions (transaction_id, card_id, merchant_name, transaction_amount, transaction_date)
- loans (loan_id, client_id, loan_amount, interest_rate, loan_status)

Return only the SQL query.
"""

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a database expert converting Cypher to SQL."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return {
        "cypher": request.cypher,
        "sql": response.choices[0].message.content.strip()
    }
```

### Frontend Integration:

Update `HomePage.jsx` to show both queries:

```jsx
// Add fourth tab
{activeTab === 'sql' && (
  <div>
    <div className="flex items-center justify-between mb-2">
      <h3 className="text-sm font-medium text-gray-700">Equivalent SQL Query</h3>
      <span className="text-xs text-gray-500">(For reference only)</span>
    </div>
    <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
      <code>{result.sql_query}</code>
    </pre>
  </div>
)}
```

## Recommended Approach

**For your use case, I recommend Option 1 (Dual Database Support)**:

### Why?
1. ✅ Most accurate - queries designed for each database
2. ✅ Better performance - native queries
3. ✅ Easier to maintain - no complex translation logic
4. ✅ Flexible - can use both graph and relational features

### Next Steps:

1. **Set up SQL database** (PostgreSQL/MySQL)
2. **Migrate data** from JSON files to SQL tables
3. **Add SQL query generation** to backend
4. **Update frontend** to show both results

Would you like me to implement this? I can:
- Create SQL schema migration scripts
- Add SQL database support to backend
- Update frontend to display both Cypher and SQL results
- Add a toggle to switch between Neo4j and SQL execution

Let me know which approach you prefer!

## Comparison Table

| Feature | Neo4j (Cypher) | SQL (Relational) |
|---------|---------------|------------------|
| **Best For** | Relationships, lineage, paths | Aggregations, transactions |
| **Queries** | Graph patterns | Table joins |
| **Performance** | Fast for connected data | Fast for simple lookups |
| **Complexity** | Simple relationship queries | Complex joins |
| **Lineage** | Native support | Requires recursive CTEs |
| **Metadata** | Graph-native | Separate catalog tables |

## Example Side-by-Side

### Question: "Show clients with loans over $50,000"

**Cypher:**
```cypher
MATCH (c:Client)-[:HAS_LOAN]->(l:Loan_record)
WHERE l.loan_amount > 50000
RETURN c.first_name, c.last_name, l.loan_amount
ORDER BY l.loan_amount DESC
```

**SQL:**
```sql
SELECT c.first_name, c.last_name, l.loan_amount
FROM clients c
JOIN loans l ON c.client_id = l.client_id
WHERE l.loan_amount > 50000
ORDER BY l.loan_amount DESC;
```

---

**Need help implementing any of these options? Let me know!**
