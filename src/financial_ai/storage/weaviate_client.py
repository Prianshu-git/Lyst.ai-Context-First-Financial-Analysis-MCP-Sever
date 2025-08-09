from __future__ import annotations

import weaviate
from weaviate.auth import AuthApiKey
from typing import Any, Dict, List, Optional

from ..config import config


class WeaviateStore:
    def __init__(self) -> None:
        auth = AuthApiKey(api_key=config.weaviate.api_key) if config.weaviate.api_key else None
        self.client = weaviate.Client(url=config.weaviate.endpoint, auth_client_secret=auth)
        # Tune batch to be gentle and avoid long waits
        self.client.batch.configure(batch_size=64, num_workers=2, dynamic=False, timeout_retries=0)
        self.class_chunk = config.weaviate.class_chunk
        self.class_table = config.weaviate.class_table

    def upsert_chunks(self, objects: List[Dict[str, Any]]) -> None:
        with self.client.batch as batch:
            for props in objects:
                batch.add_data_object(props, class_name=self.class_chunk)

    def upsert_table_cells(self, rows: List[Dict[str, Any]]) -> None:
        with self.client.batch as batch:
            for props in rows:
                batch.add_data_object(props, class_name=self.class_table)

    def create_answer_log(self, props):
        uid = self.client.data_object.create(props, class_name="AnswerLog")
        return uid

    def create_citations(self, rows):
        with self.client.batch as batch:
            batch.batch_size = 100
            for props in rows:
                batch.add_data_object(props, class_name="Citation")

    def hybrid_search(self, query: str, where: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
        # Primary: BM25 search
        props = [
            "docName", "sourceUri", "docType", "periodYear", "periodQuarter",
            "page", "lineStart", "lineEnd", "section", "text"
        ]
        q = self.client.query.get(self.class_chunk, props).with_bm25(query=query).with_limit(limit)
        if where:
            q = q.with_where(where)
        res = q.do()
        hits = res.get('data', {}).get('Get', {}).get(self.class_chunk, [])
        if hits:
            return hits
        # Fallback 1: ignore BM25, return any objects matching filter
        q2 = self.client.query.get(self.class_chunk, props).with_limit(limit)
        if where:
            q2 = q2.with_where(where)
        res2 = q2.do()
        hits2 = res2.get('data', {}).get('Get', {}).get(self.class_chunk, [])
        if hits2:
            return hits2
        # Fallback 2: return any objects globally
        res3 = self.client.query.get(self.class_chunk, props).with_limit(limit).do()
        return res3.get('data', {}).get('Get', {}).get(self.class_chunk, [])
