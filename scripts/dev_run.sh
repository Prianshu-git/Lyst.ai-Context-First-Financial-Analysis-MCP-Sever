#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=src
uvicorn financial_ai.mcp.server:app --host 0.0.0.0 --port 8088 --reload
