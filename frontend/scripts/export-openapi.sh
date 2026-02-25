#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
OUTPUT_FILE="$ROOT_DIR/frontend/packages/api-client/openapi.json"

cd "$BACKEND_DIR"

uv run python -c "import json; from pathlib import Path; from app.main import app; Path('$OUTPUT_FILE').write_text(json.dumps(app.openapi(), indent=2) + '\n', encoding='utf-8')"

echo "Exported OpenAPI schema to $OUTPUT_FILE"
