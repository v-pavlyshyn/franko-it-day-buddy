#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${FIRESTORE_LOCATION:-}" ]]; then
  echo "FIRESTORE_LOCATION is not set. Example: eur3"
  exit 1
fi

echo "Enabling required services..."
gcloud services enable       run.googleapis.com       aiplatform.googleapis.com       cloudbuild.googleapis.com       artifactregistry.googleapis.com       firestore.googleapis.com       secretmanager.googleapis.com

echo "Creating Firestore (Native) if not exists..."
set +e
gcloud firestore databases create --location="$FIRESTORE_LOCATION" --type=firestore-native
STATUS=$?
set -e
if [[ $STATUS -ne 0 ]]; then
  echo "Firestore may already exist or another issue occurred. Continuing..."
fi

echo "Done."
