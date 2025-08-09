from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


GAAP_MAP: Dict[str, str] = {
    "total current assets": "CURRENT_ASSETS",
    "current assets": "CURRENT_ASSETS",
    "total current liabilities": "CURRENT_LIABILITIES",
    "current liabilities": "CURRENT_LIABILITIES",
    "total assets": "TOTAL_ASSETS",
    "total liabilities": "TOTAL_LIABILITIES",
    "total shareholders' equity": "TOTAL_EQUITY",
    "net income": "NET_INCOME",
    "revenue": "REVENUE",
}


def normalize_label(label: str) -> str:
    key = label.strip().lower()
    return GAAP_MAP.get(key, label)


@dataclass
class StatementRef:
    statement_type: str  # IS|BS|CF
    year: int
    quarter: Optional[int]
