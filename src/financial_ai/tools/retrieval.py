from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..storage.weaviate_client import WeaviateStore


def _where_filter(tenant_id: str, company_id: str, year: Optional[int] = None, quarter: Optional[int] = None, statement: Optional[str] = None) -> Dict[str, Any]:
    operands = [
        {"path": ["tenantId"], "operator": "Equal", "valueText": tenant_id},
        {"path": ["companyId"], "operator": "Equal", "valueText": company_id},
    ]
    if year is not None:
        operands.append({"path": ["periodYear"], "operator": "Equal", "valueNumber": int(year)})
    if quarter is not None:
        operands.append({"path": ["periodQuarter"], "operator": "Equal", "valueNumber": int(quarter)})
    if statement is not None:
        operands.append({"path": ["statementType"], "operator": "Equal", "valueText": statement})
    return {"operator": "And", "operands": operands}


def retrieve_context(query: str, tenant_id: str, company_id: str, year: Optional[int] = None, quarter: Optional[int] = None, k: int = 12) -> List[Dict[str, Any]]:
    store = WeaviateStore()
    # Strict: tenant + company + optional period
    where_strict = _where_filter(tenant_id, company_id, year, quarter)
    results = store.hybrid_search(query, where=where_strict, limit=max(k, 12))
    if results:
        return results
    # Relaxed: tenant only + optional period
    where_tenant: Dict[str, Any] = {
        "operator": "And",
        "operands": [
            {"path": ["tenantId"], "operator": "Equal", "valueText": tenant_id},
        ],
    }
    if year is not None:
        where_tenant["operands"].append({"path": ["periodYear"], "operator": "Equal", "valueNumber": int(year)})
    if quarter is not None:
        where_tenant["operands"].append({"path": ["periodQuarter"], "operator": "Equal", "valueNumber": int(quarter)})
    results = store.hybrid_search(query, where=where_tenant, limit=max(k, 12))
    if results:
        return results
    # Fallback: no filter (global)
    return store.hybrid_search(query, where=None, limit=max(k, 12))


def format_context_label(obj: Dict[str, Any]) -> str:
    # Create a meaningful context label with document name and period
    doc_name = obj.get("docName", "")
    year = obj.get("periodYear")
    quarter = obj.get("periodQuarter")
    
    parts = []
    if doc_name:
        parts.append(doc_name)
    
    if year and quarter:
        parts.append(f"{year}Q{quarter}")
    elif year:
        parts.append(str(year))
    
    # If we have meaningful parts, join them
    if parts:
        return " | ".join(parts)
    
    # Fallback to source URI or unknown
    return (obj.get("sourceUri") or "Unknown source")
