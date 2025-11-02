#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo "Usage: ./scripts/push_to_github.sh <GITHUB_REPO_URL>"
  echo "Example: ./scripts/push_to_github.sh git@github.com:your-org/franko-it-day-buddy.git"
  exit 1
fi
REPO_URL="$1"
git init
git checkout -b main || true
git add .
git commit -m "Initial commit: Franko IT Day Buddy"
git remote add origin "$REPO_URL" || git remote set-url origin "$REPO_URL"
git push -u origin main
