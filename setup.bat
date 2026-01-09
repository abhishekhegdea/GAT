@echo off
echo ================================
echo Attendance System - Quick Start
echo ================================

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Python is not installed. Please install Python 3.9+
    exit /b 1
)
echo √ Python found

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Node.js is not installed. Please install Node.js 18+
    exit /b 1
)
echo √ Node.js found

echo.
echo Step 1: Configure Firebase (Firestore/Storage)
echo ================================
echo Ensure you have downloaded your Firebase service account JSON.
echo Place it at backend\firebase-service-account.json or set FIREBASE_CREDENTIALS env var.
echo.

echo.
echo Step 2: Backend Setup...
echo ================================

cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing Python dependencies...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    (
        echo FLASK_APP=app.py
        echo FLASK_ENV=development
        echo SECRET_KEY=dev_secret_key_change_in_production
        echo JWT_SECRET_KEY=dev_jwt_secret_key_change_in_production
        echo FIREBASE_CREDENTIALS=./firebase-service-account.json
        echo FIREBASE_PROJECT_ID=your_project_id
        echo FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
        echo CORS_ORIGINS=http://localhost:5173,http://localhost:3000
        echo UPLOAD_FOLDER=uploads
        echo MAX_CONTENT_LENGTH=16777216
    ) > .env
)

REM Initialize database
echo Firebase backend configured (Firestore/Storage). No SQL database needed.
echo √ Backend setup complete

echo.
echo Step 3: Frontend Setup...
echo ================================

cd ..\frontend

REM Install dependencies
echo Installing Node.js dependencies...
call npm install --silent

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating frontend .env file...
    (
        echo VITE_API_URL=http://localhost:5000/api
        echo VITE_FIREBASE_API_KEY=your_api_key
        echo VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
        echo VITE_FIREBASE_PROJECT_ID=your_project_id
        echo VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
        echo VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
        echo VITE_FIREBASE_APP_ID=your_app_id
        echo VITE_FIREBASE_MEASUREMENT_ID=your_measurement_id
    ) > .env
)

echo √ Frontend setup complete

cd ..

echo.
echo ================================
echo √ Setup Complete!
echo ================================
echo.
echo Default Admin Credentials:
echo   Email: admin@system.com
echo   Password: Admin@123
echo.
echo To start the application:
echo   1. Backend:  cd backend ^&^& venv\Scripts\activate ^&^& python app.py
echo   2. Frontend: cd frontend ^&^& npm run dev
echo.
echo Access the application at: http://localhost:5173
echo ================================

pause
