from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class WeaviateConfig:
    endpoint: str = os.getenv("WEAVIATE_ENDPOINT", "http://localhost:8080")
    api_key: Optional[str] = os.getenv("WEAVIATE_API_KEY")
    class_chunk: str = os.getenv("WEAVIATE_CLASS_CHUNK", "Chunk")
    class_table: str = os.getenv("WEAVIATE_CLASS_TABLE", "TableCell")


@dataclass
class ServiceConfig:
    tenant_id: str = os.getenv("SERVICE_TENANT_ID", "tenant-dev")
    artifacts_dir: str = os.getenv("ARTIFACTS_DIR", "artifacts")
    context_first: bool = True


@dataclass
class LLMConfig:
    provider: str = os.getenv("LLM_PROVIDER", "openai")
    model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")


@dataclass
class Config:
    weaviate: WeaviateConfig = WeaviateConfig()
    service: ServiceConfig = ServiceConfig()
    llm: LLMConfig = LLMConfig()


config = Config()

# Ensure artifacts directory exists at import time for convenience
os.makedirs(config.service.artifacts_dir, exist_ok=True)
