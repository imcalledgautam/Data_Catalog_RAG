# 🏦 Bank Data Catalog - Text-to-Cypher POC

A comprehensive data catalog system that translates natural language questions into Cypher queries for Neo4j, featuring real bank data mock-up with relationships and metadata.

## 🚀 Features

- **🤖 LLM-Powered Queries**: Natural language to Cypher translation using OpenAI GPT-4
- **📊 Rich Data Model**: Complete bank data schema with clients, accounts, transactions, loans
- **🔗 Smart Relationships**: Automatic relationship creation based on foreign keys
- **📈 Streamlit UI**: Interactive web interface for querying and visualization
- **📋 AI Summarization**: Intelligent query result summarization
- **🔍 Schema Metadata**: Table and column metadata with lineage tracking

## 📁 Project Structure

```
DataCatalog/
├── src/                    # Source code
│   ├── __init__.py        # Package initialization
│   ├── agent.py           # LLM query translation logic
│   ├── neo4j_setup.py     # Database setup and data ingestion
│   └── nasa_cmr_catalog_poc.py  # NASA CMR integration (legacy)
├── data/                   # Mock data files
│   ├── clients.json       # Client data
│   ├── bank_accounts.json # Account data
│   ├── card_details.json  # Card information
│   └── *.json            # Other mock data files
├── tests/                  # Test suite
│   ├── __init__.py        # Test package
│   └── test_queries.py    # Query validation tests
├── config/                 # Configuration files
│   └── env.example        # Environment variable template
├── docs/                   # Documentation (future)
├── main.py                # CLI execution driver
├── app.py                 # Streamlit web interface
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🛠️ Prerequisites

- **Neo4j Database**: Local Neo4j instance running on `bolt://localhost:7687`
- **OpenAI API Key**: Valid OpenAI API key for GPT-4
- **Python 3.8+**: Python environment

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd DataCatalog
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp config/env.example .env
   # Edit .env with your OpenAI API key and Neo4j credentials
   ```

4. **Start Neo4j**:
   - Ensure Neo4j is running on `bolt://localhost:7687`
   - Default credentials: `neo4j/password`

## 🎯 Usage

### 🖥️ Command Line Interface
```bash
python main.py
```
Runs the complete POC with data ingestion and example queries.

### 🌐 Web Interface (Streamlit)
```bash
streamlit run app.py
```
Launches interactive web interface at `http://localhost:8501`

### 🧪 Test Suite
```bash
python tests/test_queries.py
```
Runs comprehensive test queries to validate functionality.

## 📊 Data Model

The system includes the following data entities:

- **Clients**: Customer information and profiles
- **Bank Accounts**: Account details, balances, and types
- **Cards**: Credit/debit card information and status
- **Transactions**: Card and online transaction records
- **Loans**: Loan accounts and payment status
- **Employees**: Bank staff and branch assignments
- **Branches**: Bank branch locations and details
- **Support Tickets**: Customer service interactions

## 🔍 Example Queries

The system can answer questions like:

- "Show all clients who have a savings account"
- "List transactions above $5000 for any card"
- "Find employees working in Mumbai branches"
- "Which clients have active loans?"
- "Show card transactions for blocked cards"
- "List top 5 clients by total account balance"

## 🛠️ Development

### Running Tests
```bash
python -m pytest tests/ -v
```

### Code Structure
- `src/agent.py`: Core LLM integration and Cypher generation
- `src/neo4j_setup.py`: Database operations and data ingestion
- `main.py`: CLI interface for demo execution
- `app.py`: Streamlit web application

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Neo4j for graph database technology
- Streamlit for the web interface framework

**Setup database only**:
```bash
python neo4j_setup.py
```

**Test agent directly**:
```bash
python agent.py
```

## Graph Schema

### Nodes
- **Table**: `{name, description}` - Database tables
- **Column**: `{name, data_type}` - Table columns
- **CDE**: `{name, description}` - Critical Data Elements
- **Region**: `{name, description}` - Geographic regions

### Relationships
- **LOADS_INTO**: `{lineage_type}` - ETL lineage between tables
- **JOINS**: `{join_key}` - Join relationships with key
- **HAS_COLUMN**: Table to Column relationship
- **IS_CDE_FOR**: CDE to Column mapping
- **BELONGS_TO_REGION**: Table to Region assignment

## Example Queries

1. **Query 1**: "Show lineage and join key for the DEPOSIT_SUMMARY table."
   - Demonstrates lineage tracing with join key identification

2. **Query 2**: "Which tables are linked to CDE_00145 and what region are they for?"
   - Shows CDE tracking across tables and regions

3. **Query 3**: "What are the source tables loading into the FINAL_REPORT table?"
   - Illustrates upstream lineage discovery

## Architecture

- **neo4j_setup.py**: Creates a synthetic metadata graph with 15 nodes and 28 relationships representing Citibank data structures
- **agent.py**: Uses LangChain's GraphCypherQAChain to translate questions to Cypher and execute them
- **main.py**: Orchestrates setup and demonstrates three use cases

## Notes

- No deployment files included (as per requirements)
- No UI files included (console-based output only)
- LLM configured via OPENAI_API_KEY environment variable
- Fully executable locally with Neo4j running
