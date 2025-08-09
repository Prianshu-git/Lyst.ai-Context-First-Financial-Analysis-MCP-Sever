from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from pdfminer.high_level import extract_text

from ..config import config
from ..storage.weaviate_client import WeaviateStore

NAME_RE = re.compile(r"^(?P<name>.+)_Q(?P<q>[1-4])_(?P<year>\d{4})", re.IGNORECASE)
# Allow inferring period from parent directories like "2024q1", "2024Q2"
DIR_QY_RE = re.compile(r"^(?P<year>20\d{2})\s*[-_ ]?q(?P<q>[1-4])$", re.IGNORECASE)


def infer_metadata(file_path: Path) -> Dict[str, Optional[str]]:
    m = NAME_RE.match(file_path.stem)
    meta: Dict[str, Optional[str]] = {
        "docName": file_path.stem,
        "sourceUri": str(file_path),
        "periodYear": None,
        "periodQuarter": None,
    }
    if m:
        meta["docName"] = m.group("name")
        meta["periodYear"] = int(m.group("year"))
        meta["periodQuarter"] = int(m.group("q"))
    else:
        # Fallback: look up the directory chain for a token like "2024q1"
        for parent in file_path.parents:
            pm = DIR_QY_RE.match(parent.name)
            if pm:
                meta["periodYear"] = int(pm.group("year"))
                meta["periodQuarter"] = int(pm.group("q"))
                break
    return meta


def pdf_to_chunks(file: Path) -> List[Dict]:
    text = extract_text(str(file))
    chunks: List[Dict] = []
    # naive split by pages using form feed preserved by pdfminer when possible
    pages = text.split('\f') if '\f' in text else [text]
    for page_idx, page in enumerate(pages, start=1):
        lines = [ln.strip() for ln in page.splitlines() if ln.strip()]
        for i in range(0, len(lines), 6):
            snippet = " ".join(lines[i:i+6])
            chunks.append({
                "page": page_idx,
                "lineStart": i + 1,
                "lineEnd": min(i + 6, len(lines)),
                "section": "auto",
                "text": snippet,
            })
    return chunks


def xlsx_to_cells(file: Path) -> List[Dict]:
    rows: List[Dict] = []
    xls = pd.ExcelFile(file)
    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        for idx, row in df.iterrows():
            label = str(row.iloc[0])
            for col_idx in range(1, min(6, len(row))):
                val = row.iloc[col_idx]
                cell = {
                    "sheet": sheet,
                    "cellRange": f"{sheet}!R{idx+1}C{col_idx+1}",
                    "gaapKey": label.lower(),
                    "label": label,
                    "amount": float(val) if pd.notna(val) and isinstance(val, (int, float)) else None,
                }
                rows.append(cell)
    return rows


def ingest_path(
    path: str,
    tenant_id: Optional[str] = None,
    company_id: Optional[str] = None,
    max_files: Optional[int] = None,
    progress_every: int = 1000,
) -> int:
    store = WeaviateStore()
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    files = list(p.glob("**/*"))
    ingested = 0
    processed_files = 0
    for file in files:
        if file.is_dir():
            continue
        processed_files += 1
        if max_files is not None and processed_files > max_files:
            break
        meta = infer_metadata(file)
        meta["tenantId"] = tenant_id or config.service.tenant_id
        meta["companyId"] = company_id or str(uuid.uuid4())
        meta["documentId"] = str(uuid.uuid4())
        meta["docType"] = file.suffix.lower().lstrip('.')
        base_props = {k: v for k, v in meta.items() if v is not None}
        if file.suffix.lower() == ".pdf":
            chunks = pdf_to_chunks(file)
            for c in chunks:
                c.update(base_props)
            store.upsert_chunks(chunks)
            ingested += len(chunks)
        elif file.suffix.lower() in {".xlsx", ".xls"}:
            cells = xlsx_to_cells(file)
            for r in cells:
                r.update(base_props)
            store.upsert_table_cells(cells)
            ingested += len(cells)
        else:
            # Fallback: treat as plain text
            text = file.read_text(errors='ignore')
            chunks = []
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            for i in range(0, len(lines), 6):
                snippet = " ".join(lines[i:i+6])
                chunks.append({
                    "page": 1,
                    "lineStart": i + 1,
                    "lineEnd": min(i + 6, len(lines)),
                    "section": "auto",
                    "text": snippet,
                })
            for c in chunks:
                c.update(base_props)
            store.upsert_chunks(chunks)
            ingested += len(chunks)
        if progress_every and ingested and ingested % progress_every == 0:
            print(f"Progress: {ingested} objects upserted...")
    return ingested


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--tenant-id", default=None)
    ap.add_argument("--company-id", default=None)
    ap.add_argument("--max-files", type=int, default=None, help="Process at most N files from the tree")
    ap.add_argument("--progress-every", type=int, default=1000, help="Print a progress line every N objects")
    args = ap.parse_args()
    count = ingest_path(args.path, args.tenant_id, args.company_id, max_files=args.max_files, progress_every=args.progress_every)
    print(f"Ingested {count} objects")
