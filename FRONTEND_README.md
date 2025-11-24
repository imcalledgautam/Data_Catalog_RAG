# Bank Data Catalog - Modern Frontend + REST API

Complete full-stack implementation with React frontend and FastAPI backend.

## 🏗️ Project Structure

```
Data_Catalog_RAG/
├── backend_api.py              # FastAPI REST Backend
├── backend_requirements.txt    # Backend dependencies
├── src/                        # Original Python modules
│   ├── agent.py               # LLM Cypher generation
│   └── neo4j_setup.py         # Database setup
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── pages/            # All page components
│   │   │   ├── HomePage.jsx
│   │   │   ├── SchemaExplorer.jsx
│   │   │   ├── LineageViewer.jsx
│   │   │   └── QueryHistory.jsx
│   │   ├── services/
│   │   │   └── api.js        # Backend API client
│   │   ├── utils/
│   │   │   └── queryHistory.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── data/                       # JSON data files
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Neo4j Database (running on `bolt://localhost:7687`)
- OpenAI API Key

### Step 1: Set Up Neo4j Database

```bash
# Make sure Neo4j is running
# Default credentials: neo4j/password

# Populate the database with data
python src/neo4j_setup.py
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 3: Start the Backend API

```bash
# Install backend dependencies
pip install -r backend_requirements.txt

# Start FastAPI server
python backend_api.py

# API will be available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Step 4: Start the Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will be available at: http://localhost:5173
```

## 📱 Frontend Features

### 1. **Home Page** (`/`)
- Natural language search bar
- AI-powered Text-to-Cypher conversion
- Three-tab results view:
  - **Summary**: AI-generated business summary
  - **Results**: Data table with query results
  - **Cypher**: Generated Cypher query with copy button
- Example queries for quick testing
- Database statistics dashboard

### 2. **Schema Explorer** (`/schema`)
- Browse all tables in the metadata catalog
- Search tables by name or description
- View detailed table information:
  - Column names and data types
  - Critical Data Elements (CDE) tags
  - Region mappings (APAC, EMEA, NAM)
- Clean two-panel interface

### 3. **Lineage Viewer** (`/lineage`)
- Interactive graph visualization using React Flow
- Select any table to view its lineage
- Adjustable depth (1-5 levels)
- Visual representation of:
  - Upstream dependencies
  - Downstream consumers
  - Data flow relationships
- Zoom, pan, and minimap controls

### 4. **Query History** (`/history`)
- View all previous queries
- Search through history
- Re-examine past results
- Delete individual queries or clear all
- Stored locally in browser (localStorage)

## 🔌 REST API Endpoints

### Query Endpoints
- `POST /api/ask` - Ask a natural language question
- `POST /api/query/cypher` - Execute raw Cypher query

### Schema Endpoints
- `GET /api/schema/tables` - Get all tables
- `GET /api/schema/table/{table_name}` - Get table details
- `GET /api/search/tables?q={query}` - Search tables

### Lineage Endpoints
- `GET /api/lineage/{table_name}?depth={1-5}` - Get table lineage

### Utility Endpoints
- `GET /api/stats` - Get database statistics
- `GET /` - Health check

## 🎨 UI Technology Stack

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **TailwindCSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **React Flow** - Graph visualization
- **Lucide React** - Icon library
- **date-fns** - Date formatting

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Neo4j Python Driver** - Database connection
- **OpenAI API** - LLM integration
- **Pydantic** - Data validation

## 📝 Development Commands

### Frontend

```bash
cd frontend

# Development
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build

# Linting
npm run lint         # Run ESLint
```

### Backend

```bash
# Development
python backend_api.py              # Start with auto-reload

# Production
uvicorn backend_api:app --host 0.0.0.0 --port 8000
```

## 🔧 Configuration

### Vite Proxy Configuration
The frontend proxies `/api` requests to the backend:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

### CORS Configuration
Backend allows requests from frontend ports:

```python
# backend_api.py
allow_origins=["http://localhost:5173", "http://localhost:3000"]
```

## 📊 Data Model

### Data Nodes
- **Client**: Bank customers (500 clients)
- **Bank_account**: Customer accounts
- **Card_detail**: Credit/debit cards
- **Card_transaction**: Card transactions
- **Loan_record**: Loan information
- **Employee**: Bank employees
- **Branche**: Bank branches
- **Customer_support**: Support tickets
- **Online_transaction**: Online transactions

### Metadata Nodes
- **Table**: Data table metadata
- **Column**: Column definitions
- **CDE**: Critical Data Elements
- **Region**: Geographic regions (APAC, EMEA, NAM)

### Relationships
- `HAS_ACCOUNT`, `HAS_CARD`, `HAS_LOAN`, `HAS_TRANSACTION`
- `HAS_COLUMN`, `IS_CDE_FOR`, `BELONGS_TO_REGION`
- `LOADS_INTO` (lineage), `JOINS` (join keys)

## 🐛 Troubleshooting

### Backend Issues

**Problem**: "Connection to Neo4j failed"
```bash
# Solution: Verify Neo4j is running
neo4j status
neo4j start
```

**Problem**: "OpenAI API error"
```bash
# Solution: Check your API key in .env
echo $OPENAI_API_KEY
```

### Frontend Issues

**Problem**: "API request failed"
```bash
# Solution: Ensure backend is running on port 8000
curl http://localhost:8000/
```

**Problem**: "Module not found" errors
```bash
# Solution: Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 🚀 Production Deployment

### Backend

```bash
# Install production dependencies
pip install -r backend_requirements.txt

# Run with Gunicorn
pip install gunicorn
gunicorn backend_api:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend

```bash
cd frontend

# Build for production
npm run build

# The dist/ folder contains static files
# Deploy to: Vercel, Netlify, AWS S3, etc.
```

## 🔐 Security Notes

### Current Implementation (POC)
⚠️ This is a Proof of Concept with security limitations:

1. **Cypher Injection Risk**: LLM-generated queries run without validation
2. **No Authentication**: No user authentication or authorization
3. **No Rate Limiting**: Unlimited API calls possible
4. **Client-Side Storage**: History stored in browser localStorage

### Production Recommendations
Before deploying to production:

1. Add Cypher query validation and sanitization
2. Implement authentication (OAuth, JWT)
3. Add rate limiting middleware
4. Use secure session storage
5. Enable HTTPS
6. Add input validation and sanitization
7. Implement proper error handling
8. Add logging and monitoring
9. Use environment-specific configurations
10. Implement connection pooling

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

This is a POC project. For production use:
1. Implement security best practices
2. Add comprehensive error handling
3. Create proper test suites
4. Add logging infrastructure
5. Implement monitoring and alerting

## 📄 License

Bank Data Catalog - POC Project

---

**Built with ❤️ using React, FastAPI, Neo4j, and OpenAI GPT-4**
