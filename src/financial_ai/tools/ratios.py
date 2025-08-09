from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class RatioResult:
    metric: str
    formula: str
    value: Optional[float]
    context: str


def current_ratio(current_assets: float, current_liabilities: float) -> Optional[float]:
    if current_assets is None or current_liabilities in (None, 0):
        return None
    try:
        return float(current_assets) / float(current_liabilities)
    except ZeroDivisionError:
        return None


def compute_basic_ratios(values: Dict[str, float], context: str) -> List[RatioResult]:
    results: List[RatioResult] = []
    results.append(RatioResult("Current Ratio", "Current Assets / Current Liabilities", current_ratio(values.get("CURRENT_ASSETS"), values.get("CURRENT_LIABILITIES")), context))
    # Add stubs for extensibility
    if "NET_INCOME" in values and "TOTAL_EQUITY" in values and values.get("TOTAL_EQUITY") not in (None, 0):
        results.append(RatioResult("ROE", "Net Income / Total Equity", float(values["NET_INCOME"]) / float(values["TOTAL_EQUITY"]), context))
    if "NET_INCOME" in values and "TOTAL_ASSETS" in values and values.get("TOTAL_ASSETS") not in (None, 0):
        results.append(RatioResult("ROA", "Net Income / Total Assets", float(values["NET_INCOME"]) / float(values["TOTAL_ASSETS"]), context))
    return results
