<img width="548" height="548" alt="Gemini_Generated_Image_51bvpm51bvpm51bv" src="https://github.com/user-attachments/assets/9df16b07-fb91-4ee5-b4ac-6334153fe557" />

<div align = "center">
<h1> Lyst.ai: Context-First Financial Analysis MCP Sever </h1>
</div>

<div align = "center">
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![GraphQL](https://img.shields.io/badge/-GraphQL-E10098?style=for-the-badge&logo=graphql&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) 
</div>

## Overview

**Lyst.ai** is a context-first financial analysis platform that revolutionizes how investors, bankers, consultants, and lawyers process complex financial and legal documents. The system provides intelligent Q&A, financial ratio analysis, and automated report generation through GraphQL APIs and RESTful endpoints, enabling seamless integration with AI-powered financial analysis workflows.

### Core Philosophy: Context-First Architecture

This platform prioritizes **retrieving relevant financial context first**, then applying AI reasoning. Unlike traditional approaches that rely heavily on pre-trained models, our system:

1. **Ingests and vectors financial documents** (10-K, 10-Q, earnings reports)
2. **Retrieves precise contextual chunks** using hybrid search (BM25 + vector similarity)  
3. **Applies local LLM reasoning** (Ollama) to generate insights
4. **Produces professional Excel artifacts** with full traceability

---

## 🌟 Real-World Impact & Industry Applications

In today's financial landscape, professionals spend countless hours combing through market research, virtual data rooms, contracts, and regulatory filings to make high-stakes decisions. Our platform addresses this challenge by creating an "AI associate" that can perform in seconds what used to take entire teams days or weeks.

### Transforming Financial Workflows

**Investment Banking**: Save 30–40 hours per deal creating marketing materials, prepping for client meetings, and responding to counterparties through automated document analysis and insight generation.

**Private Credit Teams**: Automate the extraction of loan terms and covenants, eliminating days of manual contract review and reducing third-party consultation costs.

**Private Equity Firms**: Accelerate screening, due diligence, and expert network research by 20–30 hours per deal through comprehensive document synthesis.

**Law Firms**: Reduce credit agreement review time by 75%, saving thousands of dollars in legal fees per hour through automated clause interpretation and comparison.

Beyond efficiency gains, our platform enables professionals to leverage more historical data than any human could synthesize alone, using advanced context windows and multi-document analysis capabilities that were previously impossible at scale.

---

## 🏗️ Architecture Overview

The platform is built around a **distributed orchestration engine** that processes complex financial queries through multiple specialized components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client Apps   │───▶│   MCP server     │───▶│   Weaviate DB   │
│                 │    │ Graphql,Restful  │    │  (Vector Store) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Local LLM       │    │  Excel Artifacts│
                       │  (Ollama)        │    │  (Reports)      │
                       └──────────────────┘    └─────────────────┘
```
<div align = "center">
<img width="3840" height="3286" alt="Untitled diagram _ Mermaid Chart-2025-08-09-093228" src="https://github.com/user-attachments/assets/e37e3b2b-bb0a-4b66-a6b1-17abdd7ad2d2" />
</div>

### Key Components

| Component | Purpose | Technology Stack |
|-----------|---------|------------------|
| **GraphQL API** | Flexible query interface for complex financial data | GraphQL, FastAPI |
| **RESTful Endpoints** | Standard HTTP API for tool integration | FastAPI, Python 3.9+ |
| **Vector Database** | Document storage and hybrid search | Weaviate + text2vec-transformers |
| **Local LLM** | AI reasoning and insight generation | Ollama (llama3.2:1b) |
| **Ingestion Pipeline** | Document processing and vectorization | Python, regex, chunking |
| **Artifact Generation** | Professional Excel report creation | openpyxl, custom formatting |

---

## 📁 Project Structure

```
Financial-services-ai/
├── src/financial_ai/                    # Core Python package
│   ├── api/
│   │   ├── server.py                    # 🎯 Main MCP Server (GraphQL + REST)
│   │   └── graphql_schema.py            # GraphQL schema definitions
│   ├── storage/
│   │   └── weaviate_client.py           # Vector database client
│   ├── ingestion/
│   │   ├── ingest.py                    # Document ingestion pipeline
│   │   └── normalization.py             # Data cleaning and formatting
│   ├── tools/
│   │   ├── retrieval.py                 # Context retrieval logic
│   │   ├── excel_artifact.py            # Excel report generation
│   │   └── ratios.py                    # Financial ratio calculations
│   └── config.py                        # Centralized configuration
├── schemas/
│   ├── weaviate_schema.json             # Vector DB schema definition
│   ├── graphql_schema.graphql           # GraphQL schema definition
│   └── postgres.sql                     # Future relational DB schema
├── scripts/
│   ├── dev_run.sh                       # Development server launcher
│   └── apply_weaviate_schema.py         # Schema initialization script
├── data/                                # Financial documents (gitignored)
│   ├── 2024q1/                          # Quarterly financial data
│   ├── 2024q3/
│   └── 2025q2/
├── artifacts/                           # Generated Excel reports
├── docker-compose.yml                   # Infrastructure definition
└── requirements.txt                     # Python dependencies
```

---

## 🚀 Complete Setup Guide

### Prerequisites

- **Python 3.9+**
- **Docker Desktop** (for Weaviate, Ollama, and text2vec-transformers)
- **8GB+ RAM** (for local LLM)

### 1. Environment Setup

```bash
# Clone the repository
git clone <repo-url>
cd Financial-services-ai

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Upgrade pip and install dependencies
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Infrastructure Deployment

**Start the complete stack** (Weaviate + Ollama + Text2Vec):

```bash
# Launch all services
docker-compose up -d

# Verify services are running
docker-compose ps
curl http://localhost:8080/v1/meta    # Weaviate health check
curl http://localhost:11434/api/tags  # Ollama health check
```

**Services Started:**
- **Weaviate**: `localhost:8080` (Vector database)
- **Ollama**: `localhost:11434` (Local LLM)
- **Text2Vec**: `localhost:8081` (Embedding service)

### 3. Database Schema Initialization

```bash
# Apply Weaviate schema
python scripts/apply_weaviate_schema.py

# Verify schema creation
curl http://localhost:8080/v1/schema | jq '.classes[].class'
```

### 4. LLM Model Setup

```bash
# Pull the LLM model (1.3GB download)
docker-compose exec ollama ollama pull llama3.2:1b

# Verify model availability
curl http://localhost:11434/api/tags | jq '.models[].name'
```

### 5. Data Ingestion

Place your financial documents in the `data/` directory(pdf,txt,excel):

```
data/
├── 2024q1/
│   ├── 10k.txt      # Annual report
│   ├── 10q.txt      # Quarterly report
│   └── earnings.txt # Earnings transcript
└── 2024q2/
    └── ...
```

**Run ingestion:**

```bash
# Set Python path and ingest documents
export PYTHONPATH=src
python -m financial_ai.ingestion.ingest data/ \
  --tenant-id tenant-dev \
  --company-id your-company-uuid \
  --max-files 10 \
  --progress-every 5
```

### 6. Start API Server

```bash
# Development mode with auto-reload
./scripts/dev_run.sh

# Or manually:
export PYTHONPATH=src
uvicorn financial_ai.api.server:app --host 0.0.0.0 --port 8088 --reload
```

**Server available at:** 
- REST API: `http://localhost:8088`
- GraphQL Playground: `http://localhost:8088/graphql`

---

## 🔧 Detailed Module Explanations

### 1. API Server (`src/financial_ai/api/server.py`) 🎯

**The core platform component** - FastAPI application with GraphQL and REST endpoints:

```python
@app.post("/tools/qa")
async def qa(req: QARequest) -> Dict[str, Any]:
    # 1. Retrieve relevant context from Weaviate
    ctx = retrieve_context(req.question, req.tenant_id, req.company_id, ...)
    
    # 2. Generate AI insights using local LLM
    insights = _ollama_generate(prompt)
    
    # 3. Create Excel artifact with traceable evidence
    path = save_results_workbook(results_rows, citations_rows, inputs_rows)
    
    return {"artifact_uri": path, "rows": len(results_rows)}
```

**GraphQL Queries Available:**

```graphql
# Query financial data with flexible filtering
query GetFinancialData($companyId: String!, $year: Int, $quarter: Int) {
  company(id: $companyId) {
    financialData(year: $year, quarter: $quarter) {
      revenue
      assets
      liabilities
      period {
        year
        quarter
      }
    }
  }
}

# Perform contextual Q&A
query PerformQA($question: String!, $filters: FinancialFilters) {
  qa(question: $question, filters: $filters) {
    answer
    confidence
    sources {
      document
      page
      lines
    }
  }
}
```

**Available REST Endpoints:**

| Endpoint | Purpose | Input | Output |
|----------|---------|-------|--------|
| `POST /tools/qa` | Q&A with context retrieval | Question, filters | Excel artifact |
| `POST /tools/financial_summary` | Company overview | Company ID, period | Excel summary |
| `POST /tools/ratios` | Financial ratio analysis | Company ID | Calculated ratios |
| `GET /health` | Server health check | None | Status response |
| `POST /graphql` | GraphQL endpoint | GraphQL query | Flexible JSON response |

### 2. GraphQL Schema (`src/financial_ai/api/graphql_schema.py`)

**Flexible query interface** providing:

```python
type Company {
  id: ID!
  name: String
  financialData(year: Int, quarter: Int): [FinancialPeriod]
  ratios(period: PeriodInput): RatioAnalysis
}

type FinancialPeriod {
  year: Int!
  quarter: Int
  revenue: Float
  assets: Float
  liabilities: Float
  cashFlow: Float
}

type Query {
  company(id: ID!): Company
  companies(filter: CompanyFilter): [Company]
  qa(question: String!, filters: FinancialFilters): QAResult
}
```

### 3. Vector Database Client (`src/financial_ai/storage/weaviate_client.py`)

**Weaviate integration layer** providing:

- **Hybrid Search**: BM25 (keyword) + vector similarity
- **Batch Ingestion**: Optimized for large document sets
- **Schema Management**: Chunk and TableCell classes
- **GraphQL Integration**: Native GraphQL support for complex queries

```python
def hybrid_search(self, query: str, where: Optional[Dict] = None):
    # Primary: BM25 search for exact keyword matches
    q = self.client.query.get(self.class_chunk, props).with_bm25(query)
    
    # Fallback: Pure vector search if BM25 fails
    # Fallback: Global search without filters

def graphql_query(self, query: str, variables: Optional[Dict] = None):
    # Direct GraphQL queries to Weaviate
    return self.client.query.raw(query)
```

### 4. Ingestion Pipeline (`src/financial_ai/ingestion/`)

**Document processing and vectorization:**

#### `ingest.py` - Main Ingestion Logic

```python
def ingest_path(path: str, tenant_id: str, company_id: str):
    for file_path in find_files(path):
        # 1. Infer metadata from directory structure
        meta = infer_metadata(file_path)  # e.g., "2024q1" → year=2024, quarter=1
        
        # 2. Read and chunk document
        chunks = chunk_document(content, file_path, meta)
        
        # 3. Store in Weaviate with metadata
        store.upsert_chunks(chunks)
```

**Metadata Inference:**
- Directory names like `2024q1` → `periodYear=2024, periodQuarter=1`
- File extensions → `docType` (txt, pdf, xlsx)
- Automatic line numbering for traceability

#### `normalization.py` - Data Cleaning

- Text preprocessing and normalization
- Financial statement parsing
- Structured data extraction

### 5. Context Retrieval (`src/financial_ai/tools/retrieval.py`)

**Smart context retrieval with fallback strategy:**

```python
def retrieve_context(query, tenant_id, company_id, year=None, quarter=None):
    # 1. Strict search: tenant + company + period
    results = store.hybrid_search(query, where=strict_filter)
    if results: return results
    
    # 2. Relaxed search: tenant + company (any period)
    results = store.hybrid_search(query, where=relaxed_filter)
    if results: return results
    
    # 3. Global search: no filters
    return store.hybrid_search(query, where=None)
```

**Context Formatting:**
- Period labels: `num | 2025Q2`
- Source attribution: `(Doc: 10k, Page 15, Lines 1250-1275)`
- Evidence extraction: `Revenue: $1.2B USD`

### 6. Excel Artifact Generation (`src/financial_ai/tools/excel_artifact.py`)

**Professional report creation with multiple sheets:**

```python
def save_results_workbook(results_rows, citations_rows, inputs_rows):
    # Sheet 1: Results with question header
    ws_res.append([f"QUESTION: {question}", "", "", ""])
    headers = ["Context", "Evidence", "Answer", "Notes"]
    
    # Sheet 2: Citations with full metadata
    headers_cit = ["Doc Name", "Source URI", "Period", "Location", ...]
    
    # Sheet 3: Inputs & Assumptions
    # Tracks query parameters, timestamps, result counts
```

**Output Features:**
- **Question display** at top of Results sheet
- **Traceable evidence** with line numbers and document references
- **Professional formatting** with auto-sizing columns
- **Multiple sheets** for different data types

### 7. Financial Ratio Calculations (`src/financial_ai/tools/ratios.py`)

**Automated financial metric computation:**

```python
def compute_basic_ratios(values: Dict[str, float], context: str):
    return [
        RatioResult("Current Ratio", "Current Assets / Current Liabilities", ...),
        RatioResult("ROE", "Net Income / Total Equity", ...),
        RatioResult("ROA", "Net Income / Total Assets", ...)
    ]
```

### 8. Configuration Management (`src/financial_ai/config.py`)

**Centralized configuration with environment variable support:**

```python
@dataclass
class Config:
    weaviate: WeaviateConfig    # Database connection settings
    service: ServiceConfig      # Tenant ID, artifacts directory
    llm: LLMConfig             # LLM provider and model selection
```

**Environment Variables:**
- `WEAVIATE_ENDPOINT`: Vector database URL
- `OLLAMA_MODEL`: LLM model name
- `ARTIFACTS_DIR`: Output directory for Excel files

---

## 🛠️ Schema Definitions

### Weaviate Schema (`schemas/weaviate_schema.json`)

**Four main classes for financial data:**

```json
{
  "classes": [
    {
      "class": "Chunk",
      "vectorizer": "text2vec-transformers",
      "properties": [
        {"name": "tenantId", "dataType": ["text"]},
        {"name": "companyId", "dataType": ["text"]},
        {"name": "periodYear", "dataType": ["number"]},
        {"name": "periodQuarter", "dataType": ["number"]},
        {"name": "docName", "dataType": ["text"]},
        {"name": "sourceUri", "dataType": ["text"]},
        {"name": "text", "dataType": ["text"]},
        {"name": "page", "dataType": ["number"]},
        {"name": "lineStart", "dataType": ["number"]},
        {"name": "lineEnd", "dataType": ["number"]}
      ]
    }
  ]
}
```

### GraphQL Schema (`schemas/graphql_schema.graphql`)

**Complete GraphQL API schema:**

```graphql
type Query {
  company(id: ID!): Company
  companies(filter: CompanyFilter): [Company]
  qa(question: String!, filters: FinancialFilters): QAResult
  ratios(companyId: ID!, period: PeriodInput): RatioAnalysis
  financialSummary(companyId: ID!, period: PeriodInput): FinancialSummary
}

input FinancialFilters {
  tenantId: String!
  companyId: String!
  year: Int
  quarter: Int
}

input PeriodInput {
  year: Int!
  quarter: Int
}

type QAResult {
  answer: String!
  confidence: Float
  sources: [DocumentSource]
  artifactUri: String
}
```

---

## 📊 Usage Examples

### 1. GraphQL Queries

```graphql
# Complex financial data query
query GetCompanyFinancials {
  company(id: "a40bcfe3-9330-4d91-88de-b7afe9460327") {
    name
    financialData(year: 2025, quarter: 2) {
      revenue
      assets
      liabilities
      period {
        year
        quarter
      }
    }
    ratios(period: {year: 2025, quarter: 2}) {
      currentRatio
      roe
      roa
    }
  }
}

# Contextual Q&A with filters
query FinancialQA {
  qa(
    question: "What are the revenue trends and asset values?"
    filters: {
      tenantId: "tenant-dev"
      companyId: "a40bcfe3-9330-4d91-88de-b7afe9460327"
      year: 2025
      quarter: 2
    }
  ) {
    answer
    confidence
    sources {
      document
      page
      lines
    }
    artifactUri
  }
}
```

### 2. REST API Queries

```bash
curl -X POST http://localhost:8088/tools/qa \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-dev",
    "company_id": "a40bcfe3-9330-4d91-88de-b7afe9460327",
    "question": "What are the revenue trends and asset values?",
    "period": {"year": 2025, "quarter": 2}
  }'
```

**Response:**
```json
{
  "artifact_uri": "artifacts/qa_20250809_142226.xlsx",
  "rows": 6,
  "answer_log_id": "4137656b-80a2-4415-8da8-9b522144fd07"
}
```

### 3. Direct Weaviate GraphQL

```bash
# Query documents directly through Weaviate's GraphQL endpoint
curl "http://localhost:8080/v1/graphql" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ Get { Chunk(where: {path: [\"periodYear\"], operator: Equal, valueNumber: 2025}) { text periodYear periodQuarter companyId } } }"
  }'
```

### 4. Health Check

```bash
curl http://localhost:8088/health
# {"status":"ok","artifacts_dir":"artifacts"}
```

---

## 🔍 Excel Artifact Features

The generated Excel files contain:

### Results Sheet
- **Question Header**: `QUESTION: What are the revenue trends and asset values?`
- **Context Column**: `num | 2025Q2` (document + period)
- **Evidence Column**: `Revenue: 287500000.0000 USD (Doc: num, Page 1, Lines 1796869-1796874)`
- **Answer Column**: AI-generated summary
- **Notes Column**: Bullet-point insights with attribution to "Lyst.ai"

### Citations Sheet
- Full document metadata
- Source URIs and file paths
- Page numbers and line ranges
- Relevance scores

### Inputs & Assumptions Sheet
- Original question
- Query parameters
- Generation timestamp
- Result count

---

## 🧪 Development and Testing

### Running Tests

```bash
# Test document ingestion
python -m financial_ai.ingestion.ingest data/sample/ --max-files 1

# Test Q&A endpoint
curl -X POST http://localhost:8088/tools/qa \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"tenant-dev","company_id":"test-uuid","question":"revenue"}'

# Test GraphQL endpoint
curl -X POST http://localhost:8088/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ companies { id name } }"}'

# Verify Weaviate data
curl "http://localhost:8080/v1/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ Get { Chunk(limit:3){ text periodYear periodQuarter } } }"}'
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
./scripts/dev_run.sh
```

### Performance Monitoring

```bash
# Check ingestion progress
python -m financial_ai.ingestion.ingest data/ --progress-every 10

# Monitor Weaviate performance
curl http://localhost:8080/v1/meta
```

---

## 🏗️ Production Considerations

### Scaling

- **Weaviate**: Can scale horizontally with clustering
- **Ollama**: GPU acceleration for faster inference
- **API Server**: Deploy with Gunicorn/uWSGI for production
- **GraphQL**: Built-in query optimization and caching

### Security

- Add authentication to API endpoints
- Secure Weaviate with API keys
- Implement tenant isolation
- GraphQL query depth limiting

### Monitoring

- Add structured logging
- Implement health checks for all services
- Monitor artifact generation performance
- GraphQL query analytics

---

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-tool`
3. **Add your API endpoint** in `src/financial_ai/api/server.py`
4. **Update GraphQL schema** in `schemas/graphql_schema.graphql`
5. **Test thoroughly** with real financial data
6. **Submit pull request**

### Adding New API Tools

```python
@app.post("/tools/your_new_tool")
async def your_new_tool(req: YourRequest) -> Dict[str, Any]:
    # 1. Validate input
    # 2. Retrieve context if needed
    # 3. Process with LLM or calculations
    # 4. Generate artifact
    # 5. Log and return

# Add corresponding GraphQL resolver
async def resolve_your_new_tool(root, info, **args):
    # GraphQL resolver logic
    return your_new_tool_result
```

---

## 📚 Technical References

- **GraphQL Specification**: [GraphQL.org](https://graphql.org/learn/)
- **Weaviate GraphQL**: [Vector Database GraphQL API](https://weaviate.io/developers/weaviate/api/graphql)
- **Ollama Models**: [Local LLM Setup](https://ollama.ai/library)
- **FastAPI**: [Python Web Framework](https://fastapi.tiangolo.com/)

---

## 📄 Sample Outputs

<img width="881" height="139" alt="Screenshot 2025-08-09 at 7 00 20 PM" src="https://github.com/user-attachments/assets/cb1b7171-295b-42b4-9231-9146d6d61194" />
<img width="895" height="589" alt="Screenshot 2025-08-09 at 2 30 09 PM" src="https://github.com/user-attachments/assets/35e479b2-5b5c-4c7c-9663-f262c81782f4" />
<img width="939" height="226" alt="Screenshot 2025-08-09 at 2 19 17 PM" src="https://github.com/user-attachments/assets/89d1c658-f6d1-40be-81a7-ae52ff30e340" />

---

**Financial Services AI** transforms financial document analysis through context-first AI reasoning, delivered via modern GraphQL and REST APIs. The platform enables financial professionals to achieve unprecedented efficiency in document analysis, deal structuring, and regulatory compliance, providing the same transformative capabilities that are revolutionizing the financial services industry. The system prioritizes accuracy, traceability, and professional presentation, making it the ideal solution for investment banks, law firms, private equity, and financial consulting organizations seeking to leverage AI for competitive advantage.
