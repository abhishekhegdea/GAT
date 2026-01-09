#!/bin/bash

echo "================================"
echo "Attendance System - Quick Start"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi
echo "✓ Python found"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi
echo "✓ Node.js found"

echo ""
echo "Step 1: Configure Firebase (Firestore/Storage)"
echo "================================"
echo "Ensure you have downloaded your Firebase service account JSON."
echo "Place it at backend/firebase-service-account.json or set FIREBASE_CREDENTIALS env var."
echo ""

echo ""
echo "Step 2: Backend Setup..."
echo "================================"

cd backend || exit

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
FIREBASE_CREDENTIALS=./firebase-service-account.json
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
EOF
fi

echo "Firebase backend configured (Firestore/Storage). No SQL database needed."
echo "✓ Backend setup complete"

echo ""
echo "Step 3: Frontend Setup..."
echo "================================"

cd ../frontend || exit

# Install dependencies
echo "Installing Node.js dependencies..."
npm install --silent

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    cat > .env << EOF
VITE_API_URL=http://localhost:5000/api
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
VITE_FIREBASE_MEASUREMENT_ID=your_measurement_id
EOF
fi

echo "✓ Frontend setup complete"

echo ""
echo "================================"
echo "✓ Setup Complete!"
echo "================================"
echo ""
echo "Default Admin Credentials:"
echo "  Email: admin@system.com"
echo "  Password: Admin@123"
echo ""
echo "To start the application:"
echo "  1. Backend:  cd backend && source venv/bin/activate && python app.py"
echo "  2. Frontend: cd frontend && npm run dev"
echo ""
echo "Access the application at: http://localhost:5173"
echo "================================"
