from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import os
import requests
from datetime import datetime

from ..config import config
from ..tools.retrieval import retrieve_context, format_context_label
from ..tools.excel_artifact import save_results_workbook
from ..storage.weaviate_client import WeaviateStore
from ..tools.ratios import compute_basic_ratios

app = FastAPI(title="Financial AI MCP", version="0.1.0")
def _timestamped_filename(prefix: str, ext: str = "xlsx") -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.{ext}"


def _ollama_generate(prompt: str) -> str:
    """Generate text using local Ollama server if available, else fallback."""
    try:
        model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("response", "") or ""
        return ""
    except Exception:
        return ""


def _format_evidence(obj: Dict[str, Any]) -> str:
    """Format evidence text to be human-readable with location info."""
    text = obj.get("text", "")
    if not text:
        return "No text available"
    
    # Extract meaningful parts from the raw data
    lines = text.replace('\t', ' | ').split('\n')
    readable_lines = []
    
    for line in lines[:2]:  # Take first 2 lines max for cleaner output
        if line.strip():
            # Clean up tab-separated data to be more readable
            parts = line.split(' | ')
            if len(parts) >= 3:
                # Try to extract meaningful info: concept name, value, currency
                concept = parts[1] if len(parts) > 1 else ""
                # Look for numeric values in the parts
                value_parts = [p.strip() for p in parts if any(c.isdigit() for c in p) and not p.strip().isdigit() or '.' in p]
                currency_parts = [p.strip() for p in parts if p.strip() in ['USD', 'KRW', 'CNY', 'AUD', 'EUR']]
                
                if concept and value_parts:
                    currency = f" {currency_parts[0]}" if currency_parts else ""
                    readable_lines.append(f"{concept}: {value_parts[-1]}{currency}")
                elif concept:
                    readable_lines.append(concept)
    
    # Add location info
    location_parts = []
    doc_name = obj.get("docName", "")
    if doc_name:
        location_parts.append(f"Doc: {doc_name}")
    if obj.get("page"):
        location_parts.append(f"Page {obj['page']}")
    if obj.get("lineStart") and obj.get("lineEnd"):
        location_parts.append(f"Lines {obj['lineStart']}-{obj['lineEnd']}")
    
    location_str = f" ({', '.join(location_parts)})" if location_parts else ""
    
    if readable_lines:
        return f"{' | '.join(readable_lines)}{location_str}"
    else:
        # Fallback: extract first meaningful financial term
        import re
        financial_terms = re.findall(r'(Revenue|Assets|Liabilities|Income|Equity|Cash|Investment)[A-Za-z]*', text)
        if financial_terms:
            return f"Financial data: {financial_terms[0]}{location_str}"
        else:
            return f"{text[:80]}...{location_str}"


class Period(BaseModel):
    year: Optional[int] = None
    quarter: Optional[int] = None


class SummaryRequest(BaseModel):
    tenant_id: str
    company_id: str
    period: Optional[Period] = None
    output: str = "xlsx"
    question: str = "Summarize financial health"


@app.post("/tools/financial_summary")
async def financial_summary(req: SummaryRequest) -> Dict[str, Any]:
    store = WeaviateStore()
    ctx = retrieve_context(req.question, req.tenant_id, req.company_id, req.period.year if req.period else None, req.period.quarter if req.period else None)
    results_rows: List[Dict[str, Any]] = []
    citations_rows: List[Dict[str, Any]] = []

    for obj in ctx[:6]:
        label = format_context_label(obj)
        quote = obj.get("text", "")[:200]
        results_rows.append({"context": label, "evidence": quote, "answer": "See summary point", "notes": "Auto-summary seed"})
        citations_rows.append({
            "doc_name": obj.get("docName"),
            "source_uri": obj.get("sourceUri"),
            "doc_type": obj.get("docType"),
            "statement_type": obj.get("statementType"),
            "year": obj.get("periodYear"),
            "quarter": obj.get("periodQuarter"),
            "page": obj.get("page"),
            "line_start": obj.get("lineStart"),
            "line_end": obj.get("lineEnd"),
            "sheet": obj.get("sheet"),
            "cell_range": obj.get("cellRange"),
            "quote": quote,
            "chunk_id": obj.get("_additional", {}).get("id"),
            "score": obj.get("_additional", {}).get("score"),
        })

    path = save_results_workbook(results_rows, citations_rows, filename=_timestamped_filename("financial_summary"))
    # log
    log_id = store.create_answer_log({"tenantId": req.tenant_id, "companyId": req.company_id, "question": req.question, "answerText": "summary created", "artifactUri": path, "tool": "financial_summary"})
    for c in citations_rows:
        c.update({"tenantId": req.tenant_id, "companyId": req.company_id, "answerLogId": log_id})
    store.create_citations(citations_rows)
    return {"artifact_uri": path, "rows": len(results_rows), "answer_log_id": log_id}


class QARequest(BaseModel):
    tenant_id: str
    company_id: str
    question: str
    period: Optional[Period] = None


@app.post("/tools/qa")
async def qa(req: QARequest) -> Dict[str, Any]:
    store = WeaviateStore()
    ctx = retrieve_context(req.question, req.tenant_id, req.company_id, req.period.year if req.period else None, req.period.quarter if req.period else None)
    # Build a compact prompt from top-k contexts
    k = 6
    contexts: List[Dict[str, Any]] = ctx[:k]
    joined_ctx = "\n\n".join([f"[{i+1}] {format_context_label(o)}\n{(o.get('text') or '')[:480]}" for i, o in enumerate(contexts)])
    prompt = (
        f"You are a financial analyst at Lyst.ai. Provide concise numeric bullet insights strictly from the context."
        f"\nQuestion: {req.question}\n\nContext:\n{joined_ctx}\n\n"
        f"Reply ONLY as bullet lines like '- Revenue up by 10%', '- Operating expenses decreased by 2%'."
    )
    notes_bullets = _ollama_generate(prompt) or ""

    # Prepare rows: one row per context with evidence quote; answer column keeps bullets only on first row
    results_rows: List[Dict[str, Any]] = []
    citations_rows: List[Dict[str, Any]] = []
    if contexts:
        for idx, o in enumerate(contexts):
            results_rows.append({
                "context": format_context_label(o),
                "evidence": _format_evidence(o),
                "answer": "" if idx > 0 else "Summary",  # keep Answer concise
                "notes": notes_bullets if idx == 0 else "",
            })
            citations_rows.append({
                "doc_name": o.get("docName"),
                "source_uri": o.get("sourceUri"),
                "doc_type": o.get("docType"),
                "statement_type": o.get("statementType"),
                "year": o.get("periodYear"),
                "quarter": o.get("periodQuarter"),
                "page": o.get("page"),
                "line_start": o.get("lineStart"),
                "line_end": o.get("lineEnd"),
                "sheet": o.get("sheet"),
                "cell_range": o.get("cellRange"),
                "quote": (o.get("text") or "")[:200],
                "chunk_id": o.get("_additional", {}).get("id") if o else None,
                "score": o.get("_additional", {}).get("score") if o else None,
            })
    else:
        results_rows.append({
            "context": "No context found",
            "evidence": None,
            "answer": notes_bullets or "No insights",
            "notes": "",
        })

    # Add inputs for context
    inputs_rows = [
        {"key": "Question", "value": req.question},
        {"key": "Period", "value": f"{req.period.year}Q{req.period.quarter}" if req.period and req.period.year and req.period.quarter else "All periods"},
        {"key": "Company ID", "value": req.company_id},
        {"key": "Generated", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        {"key": "Results Count", "value": str(len(results_rows))},
    ]
    
    path = save_results_workbook(results_rows, citations_rows, inputs_rows, filename=_timestamped_filename("qa"))
    log_id = store.create_answer_log({"tenantId": req.tenant_id, "companyId": req.company_id, "question": req.question, "answerText": (notes_bullets or ""), "artifactUri": path, "tool": "qa"})
    for c in citations_rows:
        c.update({"tenantId": req.tenant_id, "companyId": req.company_id, "answerLogId": log_id})
    store.create_citations(citations_rows)
    return {"artifact_uri": path, "rows": len(results_rows), "answer_log_id": log_id}


class RatioRequest(BaseModel):
    tenant_id: str
    company_id: str
    period: Optional[Period] = None


@app.post("/tools/ratios")
async def ratios(req: RatioRequest) -> Dict[str, Any]:
    # This demo extracts rough values from retrieved text; production should read structured tables
    ctx = retrieve_context("current assets liabilities net income equity assets", req.tenant_id, req.company_id, req.period.year if req.period else None, req.period.quarter if req.period else None)
    values: Dict[str, float] = {}
    for obj in ctx[:20]:
        t = (obj.get("text") or "").lower()
        for key in ["current assets", "current liabilities", "net income", "total assets", "total shareholders' equity"]:
            if key in t:
                # naive parse number
                import re
                m = re.search(r"(-?\d+[\d,\.\s]*)", t)
                if m:
                    num = m.group(1).replace(",", "").strip()
                    try:
                        values[key.upper()] = float(num)
                    except ValueError:
                        pass
    context_label = format_context_label(ctx[0]) if ctx else "Unknown"
    results = compute_basic_ratios({
        "CURRENT_ASSETS": values.get("CURRENT ASSETS"),
        "CURRENT_LIABILITIES": values.get("CURRENT LIABILITIES"),
        "NET_INCOME": values.get("NET INCOME"),
        "TOTAL_ASSETS": values.get("TOTAL ASSETS"),
        "TOTAL_EQUITY": values.get("TOTAL SHAREHOLDERS' EQUITY"),
    }, context_label)

    results_rows = [{"context": r.context, "evidence": "", "answer": r.value, "notes": r.formula} for r in results]
    citations_rows: List[Dict[str, Any]] = []
    path = save_results_workbook(results_rows, citations_rows, filename="ratios.xlsx")
    return {"artifact_uri": path, "rows": len(results_rows)}


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "artifacts_dir": config.service.artifacts_dir}
