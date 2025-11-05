#!/usr/bin/env bash
set -euo pipefail
PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
RUN_REGION=${RUN_REGION:-europe-central2}
ARTIFACT_REGION=${ARTIFACT_REGION:-europe}
SERVICE=${SERVICE:-itday-buddy}
REPO=${REPO:-demos}
SQL_INSTANCE=${SQL_INSTANCE:-franko-it-day}

echo "Project: $PROJECT_ID"

echo "1) Delete Cloud Run service"
gcloud run services delete "$SERVICE" --region="$RUN_REGION" --quiet || true

echo "2) Delete Artifact Registry repo (optional)"
gcloud artifacts repositories delete "$REPO" --location="$ARTIFACT_REGION" --quiet || true

echo "3) Firestore cleanup (messages & faq)"
export PROJECT_ID
python "$(dirname "$0")/firestore_cleanup.py" || true

echo "4) (Optional) Delete Cloud SQL instance"
gcloud sql instances delete "$SQL_INSTANCE" --quiet || true

echo "5) (Optional) Disable APIs"
gcloud services disable aiplatform.googleapis.com --quiet || true
gcloud services disable run.googleapis.com --quiet || true

echo "6) (Optional) Delete service account"
gcloud iam service-accounts delete itday-buddy-sa@$PROJECT_ID.iam.gserviceaccount.com --quiet || true

echo "Cleanup complete ✅"
