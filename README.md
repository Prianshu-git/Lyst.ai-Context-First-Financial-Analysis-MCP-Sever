# Financial Services AI: MCP-Based Financial Analysis Platform

## Overview

**Financial Services AI** is a context-first financial analysis platform built around the **Model Context Protocol (MCP) server** as its core MVP. The system provides intelligent Q&A, financial ratio analysis, and automated report generation through a RESTful API that serves as an MCP server, enabling seamless integration with AI-powered financial analysis workflows.

### Core Philosophy: Context-First Architecture

This platform prioritizes **retrieving relevant financial context first**, then applying AI reasoning. Unlike traditional approaches that rely heavily on pre-trained models, our system:

1. **Ingests and vectors financial documents** (10-K, 10-Q, earnings reports)
2. **Retrieves precise contextual chunks** using hybrid search (BM25 + vector similarity)  
3. **Applies local LLM reasoning** (Ollama) to generate insights
4. **Produces professional Excel artifacts** with full traceability

---

## 🏗️ Architecture Overview

### MCP Server as MVP

The **MCP (Model Context Protocol) server** (`src/financial_ai/mcp/server.py`) is the heart of the system, exposing RESTful endpoints that implement financial analysis tools:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client Apps   │───▶│   MCP Server     │───▶│   Weaviate DB   │
│                 │    │  (FastAPI)       │    │  (Vector Store) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Local LLM       │    │  Excel Artifacts│
                       │  (Ollama)        │    │  (Reports)      │
                       └──────────────────┘    └─────────────────┘
```

### Key Components

| Component | Purpose | Technology Stack |
|-----------|---------|------------------|
| **MCP Server** | RESTful API endpoints for financial tools | FastAPI, Python 3.9+ |
| **Vector Database** | Document storage and hybrid search | Weaviate + text2vec-transformers |
| **Local LLM** | AI reasoning and insight generation | Ollama (llama3.2:1b) |
| **Ingestion Pipeline** | Document processing and vectorization | Python, regex, chunking |
| **Artifact Generation** | Professional Excel report creation | openpyxl, custom formatting |

---

## 📁 Project Structure

```
Financial-services-ai/
├── src/financial_ai/                    # Core Python package
│   ├── mcp/
│   │   └── server.py                    # 🎯 MCP SERVER (MVP)
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
│   ├── mcp_tools.json                   # MCP tool specifications
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

Place your financial documents in the `data/` directory:

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

### 6. Start MCP Server

```bash
# Development mode with auto-reload
./scripts/dev_run.sh

# Or manually:
export PYTHONPATH=src
uvicorn financial_ai.mcp.server:app --host 0.0.0.0 --port 8088 --reload
```

**Server available at:** `http://localhost:8088`

---

## 🔧 Detailed Module Explanations

### 1. MCP Server (`src/financial_ai/mcp/server.py`) 🎯

**The MVP component** - FastAPI application exposing financial analysis tools:

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

**Available Endpoints:**

| Endpoint | Purpose | Input | Output |
|----------|---------|-------|--------|
| `POST /tools/qa` | Q&A with context retrieval | Question, filters | Excel artifact |
| `POST /tools/financial_summary` | Company overview | Company ID, period | Excel summary |
| `POST /tools/ratios` | Financial ratio analysis | Company ID | Calculated ratios |
| `GET /health` | Server health check | None | Status response |

### 2. Vector Database Client (`src/financial_ai/storage/weaviate_client.py`)

**Weaviate integration layer** providing:

- **Hybrid Search**: BM25 (keyword) + vector similarity
- **Batch Ingestion**: Optimized for large document sets
- **Schema Management**: Chunk and TableCell classes

```python
def hybrid_search(self, query: str, where: Optional[Dict] = None):
    # Primary: BM25 search for exact keyword matches
    q = self.client.query.get(self.class_chunk, props).with_bm25(query)
    
    # Fallback: Pure vector search if BM25 fails
    # Fallback: Global search without filters
```

### 3. Ingestion Pipeline (`src/financial_ai/ingestion/`)

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

### 4. Context Retrieval (`src/financial_ai/tools/retrieval.py`)

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

### 5. Excel Artifact Generation (`src/financial_ai/tools/excel_artifact.py`)

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

### 6. Financial Ratio Calculations (`src/financial_ai/tools/ratios.py`)

**Automated financial metric computation:**

```python
def compute_basic_ratios(values: Dict[str, float], context: str):
    return [
        RatioResult("Current Ratio", "Current Assets / Current Liabilities", ...),
        RatioResult("ROE", "Net Income / Total Equity", ...),
        RatioResult("ROA", "Net Income / Total Assets", ...)
    ]
```

### 7. Configuration Management (`src/financial_ai/config.py`)

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

### MCP Tools Schema (`schemas/mcp_tools.json`)

**Tool definitions for the MCP server:**

- `qa`: Question answering with context retrieval
- `financial_summary`: Company overview generation  
- `ratio_benchmark`: Financial ratio analysis
- `cashflow_insights`: Cash flow analysis
- `scenario_monte_carlo`: Monte Carlo simulations
- `risk_compliance`: Compliance checking

---

## 📊 Usage Examples

### 1. Basic Q&A Query

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

### 2. Financial Summary

```bash
curl -X POST http://localhost:8088/tools/financial_summary \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-dev",
    "company_id": "company-uuid",
    "period": {"year": 2024, "quarter": 4}
  }'
```

### 3. Health Check

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
- **MCP Server**: Deploy with Gunicorn/uWSGI for production

### Security

- Add authentication to MCP endpoints
- Secure Weaviate with API keys
- Implement tenant isolation

### Monitoring

- Add structured logging
- Implement health checks for all services
- Monitor artifact generation performance

---

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-tool`
3. **Add your MCP tool** in `src/financial_ai/mcp/server.py`
4. **Update schemas** in `schemas/mcp_tools.json`
5. **Test thoroughly** with real financial data
6. **Submit pull request**

### Adding New MCP Tools

```python
@app.post("/tools/your_new_tool")
async def your_new_tool(req: YourRequest) -> Dict[str, Any]:
    # 1. Validate input
    # 2. Retrieve context if needed
    # 3. Process with LLM or calculations
    # 4. Generate artifact
    # 5. Log and return
```

---

## 📚 Technical References

- **MCP Protocol**: [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- **Weaviate Documentation**: [Vector Database Guide](https://weaviate.io/developers/weaviate)
- **Ollama Models**: [Local LLM Setup](https://ollama.ai/library)
- **FastAPI**: [Python Web Framework](https://fastapi.tiangolo.com/)

---

## 📄 License

MIT License - see LICENSE file for details.

---

**Financial Services AI** transforms financial document analysis through context-first AI reasoning, delivered via a robust MCP server architecture. The system prioritizes accuracy, traceability, and professional presentation, making it ideal for financial analysts, researchers, and AI-powered financial applications.
