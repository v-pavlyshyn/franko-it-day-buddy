#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID=$(gcloud config get-value project)
REGION=europe
RUN_REGION=europe-central2
REPO=demos
IMAGE=europe-docker.pkg.dev/$PROJECT_ID/$REPO/itday-buddy:v1

echo "Creating Artifact Registry repo if missing..."
gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION --description="workshop repo" || true

echo "Building image with Cloud Build..."
gcloud builds submit --tag $IMAGE

echo "Deploying to Cloud Run..."
gcloud run deploy itday-buddy --image=$IMAGE --region=$RUN_REGION --allow-unauthenticated --max-instances=1
