#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r api/requirements.txt

export $(grep -v '^#' .env | xargs)
uvicorn api.main:app --reload --port 8080
