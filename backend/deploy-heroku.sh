#!/bin/bash

# Deploy to Heroku
# Usage: ./deploy-heroku.sh <app-name>

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_NAME=${1:-geo-attendance-api}

echo -e "${BLUE}🚀 Deploying to Heroku...${NC}"
echo "App: $APP_NAME"

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo -e "${RED}❌ Heroku CLI not found. Install it from: https://devcenter.heroku.com/articles/heroku-cli${NC}"
    exit 1
fi

# Login to Heroku
echo -e "${BLUE}🔐 Logging into Heroku...${NC}"
heroku login

# Create app if it doesn't exist
echo -e "${BLUE}📝 Creating/verifying Heroku app...${NC}"
heroku apps:create $APP_NAME || echo "App already exists"

# Add Heroku buildpack for Python
echo -e "${BLUE}🔨 Setting buildpacks...${NC}"
heroku buildpacks:set heroku/python --app $APP_NAME

# Set environment variables
echo -e "${BLUE}⚙️  Setting environment variables...${NC}"
heroku config:set FLASK_ENV=production --app $APP_NAME
heroku config:set PYTHONUNBUFFERED=1 --app $APP_NAME

echo -e "${BLUE}📦 Please configure these environment variables in Heroku Dashboard:${NC}"
echo "  - FIREBASE_PROJECT_ID"
echo "  - FIREBASE_STORAGE_BUCKET"
echo "  - FIREBASE_CREDENTIALS (contents of JSON file)"
echo "  - SECRET_KEY"
echo "  - JWT_SECRET_KEY"
echo "  - CORS_ORIGINS"

# Deploy
echo -e "${BLUE}📤 Deploying to Heroku...${NC}"
git push heroku main || git push heroku master

# Get app URL
echo -e "${BLUE}🔗 Retrieving app URL...${NC}"
APP_URL=$(heroku apps:info $APP_NAME --shell | grep web_url | cut -d= -f2)

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}API URL: $APP_URL${NC}"
echo -e "\n${BLUE}Useful commands:${NC}"
echo "  Logs: heroku logs --tail --app $APP_NAME"
echo "  SSH: heroku run bash --app $APP_NAME"
echo "  Restart: heroku restart --app $APP_NAME"
echo "  Scale: heroku ps:scale web=2 --app $APP_NAME"
