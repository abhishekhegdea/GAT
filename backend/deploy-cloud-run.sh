#!/bin/bash

# Deploy to Google Cloud Run
# Usage: ./deploy-cloud-run.sh <project-id> <service-name> [region]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${1:-geo-attendance}
SERVICE_NAME=${2:-geo-attendance-api}
REGION=${3:-us-central1}

echo -e "${BLUE}🚀 Deploying to Google Cloud Run...${NC}"
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Install it from: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

# Set project
echo -e "${BLUE}📋 Setting GCP project...${NC}"
gcloud config set project $PROJECT_ID

# Build image
echo -e "${BLUE}🔨 Building Docker image...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Deploy to Cloud Run
echo -e "${BLUE}📤 Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --set-env-vars "FIREBASE_PROJECT_ID=$PROJECT_ID"

# Get service URL
echo -e "${BLUE}🔗 Retrieving service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}API URL: $SERVICE_URL${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo "1. Update frontend .env with API_URL=$SERVICE_URL/api"
echo "2. Update CORS_ORIGINS in backend .env"
echo "3. Test with: curl $SERVICE_URL/api/health"
