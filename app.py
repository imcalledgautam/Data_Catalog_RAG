"""
Streamlit UI for Bank Data Catalog - Text-to-Cypher Query System
"""

import streamlit as st
from src.neo4j_setup import Neo4jSetup
from src.agent import generate_lineage_response
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def summarize_results(question, results, cypher_query):
    """Use LLM to summarize query results in a concise way with aggregation."""
    if not OPENAI_API_KEY:
        return "OpenAI API key not configured. Cannot generate summary."
    
    if not results:
        return "No results found for this query."
    
    # Prepare results for summarization (limit to first 20 for context)
    results_sample = results[:20]
    results_text = "\n".join([str(record) for record in results_sample])
    
    prompt = f"""
You are a data analyst summarizing database query results for business users.

Original Question: {question}

Cypher Query Executed: {cypher_query}

Query Results ({len(results)} total records):
{results_text}

Task: Provide a concise business summary with:
1. A brief answer to the question (2-3 sentences)
2. Key aggregated insights (counts, totals, patterns)
3. Notable findings or highlights

Keep it professional and focused on business value.
"""
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        r = requests.post("https://api.openai.com/v1/chat/completions", 
                         headers=headers, json=body, timeout=60)
        
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        else:
            return f"Error generating summary: {r.status_code}"
            
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def execute_query(question):
    """Execute a natural language query and return results."""
    setup = Neo4jSetup()
    
    try:
        # Generate Cypher using LLM
        explanation, cypher = generate_lineage_response(question)
        
        if not cypher or cypher.startswith("Error") or cypher.startswith("OPENAI"):
            return None, None, explanation, []
        
        # Execute the query
        with setup.driver.session() as session:
            result = session.run(cypher)
            records = [dict(record) for record in result]
        
        return cypher, explanation, None, records
        
    except Exception as e:
        return None, None, f"Error executing query: {str(e)}", []
    finally:
        setup.close()


# Streamlit UI Configuration
st.set_page_config(
    page_title="Bank Data Catalog - Text-to-Cypher",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Bank Data Catalog Query System")
st.markdown("### Natural Language to Cypher Query Interface")

# Sidebar with predefined queries
st.sidebar.header("📋 Example Queries")
st.sidebar.markdown("Select a predefined query or write your own:")

predefined_queries = {
    "Clients with Savings Accounts": "Show all clients who have a savings account.",
    "High-Value Transactions": "List all transactions above $5000 for any card.",
    "Mumbai Branch Employees": "Find all employees working in branches located in Mumbai.",
    "Active Loans": "Which clients have active loans?",
    "Blocked Card Transactions": "Show all card transactions for blocked cards.",
    "Top Clients by Balance": "List the top 5 clients by total account balance.",
    "Checking + Credit Card": "Find all clients with both a checking account and a credit card.",
    "Open Support Tickets": "Show all customer support tickets that are still open.",
    "Account Types Distribution": "How many accounts are there for each account category?",
    "Recent Loan Applications": "Show clients who got loans in 2025.",
}

# Query selection
query_option = st.sidebar.selectbox(
    "Choose a query:",
    ["Custom Query"] + list(predefined_queries.keys())
)

# Query input
if query_option == "Custom Query":
    user_question = st.text_area(
        "Enter your question:",
        placeholder="e.g., Show me all clients with loans over $50,000",
        height=100
    )
else:
    user_question = st.text_area(
        "Selected Question:",
        value=predefined_queries[query_option],
        height=100
    )

# Execute button
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    execute_btn = st.button("🚀 Execute Query", type="primary")
with col2:
    clear_btn = st.button("🗑️ Clear")

if clear_btn:
    st.rerun()

# Execute query
if execute_btn and user_question:
    with st.spinner("Generating and executing Cypher query..."):
        cypher, explanation, error, records = execute_query(user_question)
    
    if error:
        st.error(f"❌ {error}")
    else:
        # Display results in tabs
        tab1, tab2, tab3 = st.tabs(["📊 Summary", "🔍 Raw Results", "💻 Cypher Query"])
        
        with tab1:
            st.subheader("AI Summary")
            with st.spinner("Generating summary..."):
                summary = summarize_results(user_question, records, cypher)
            st.info(summary)
            
            # Show count
            st.metric("Total Records Found", len(records))
        
        with tab2:
            st.subheader("Query Results")
            if records:
                # Display as dataframe if possible
                try:
                    import pandas as pd
                    df = pd.DataFrame(records)
                    st.dataframe(df, use_container_width=True)
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name="query_results.csv",
                        mime="text/csv"
                    )
                except:
                    # Fallback to JSON display
                    st.json(records[:50])  # Limit to 50 for display
                    if len(records) > 50:
                        st.info(f"Showing first 50 of {len(records)} records")
            else:
                st.warning("No results found.")
        
        with tab3:
            st.subheader("Generated Cypher Query")
            st.code(cypher, language="cypher")
            st.caption(f"Explanation: {explanation}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 About")
st.sidebar.info(
    """
    This application uses:
    - **Neo4j** for graph database
    - **OpenAI GPT-4** for natural language to Cypher translation
    - **Streamlit** for the user interface
    
    Ask questions in plain English and get structured data insights!
    """
)

# Connection status
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 System Status")

try:
    setup = Neo4jSetup()
    with setup.driver.session() as session:
        count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
    setup.close()
    st.sidebar.success(f"✅ Connected to Neo4j\n\n{count:,} nodes in database")
except Exception as e:
    st.sidebar.error(f"❌ Neo4j connection failed\n\n{str(e)}")

if OPENAI_API_KEY:
    st.sidebar.success("✅ OpenAI API configured")
else:
    st.sidebar.error("❌ OpenAI API key missing")
