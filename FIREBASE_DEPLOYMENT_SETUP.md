# Firebase Deployment Setup Guide

This guide walks you through setting up Firebase for production deployment.

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Enter project name: `geo-attendance-system`
4. Accept terms and click **"Create project"**
5. Wait for project creation to complete

## Step 2: Set Up Firestore Database

1. In Firebase Console, click **"Firestore Database"** in left menu
2. Click **"Create database"**
3. Select **"Start in production mode"** for deployment
4. Choose region closest to your users (e.g., `us-central1`)
5. Click **"Enable"**
6. Wait for database initialization

## Step 3: Set Up Cloud Storage

1. Click **"Storage"** in left menu
2. Click **"Get Started"**
3. Accept default security rules (we'll update them)
4. Choose region matching your Firestore (e.g., `us-central1`)
5. Click **"Done"**

## Step 4: Create Service Account

1. Click **"Project Settings"** (gear icon)
2. Go to **"Service accounts"** tab
3. Click **"Generate new private key"**
4. Save the JSON file as `firebase-credentials.json` in backend folder

## Step 5: Update Environment Variables

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` with your Firebase credentials:
```dotenv
# Firebase Configuration
FIREBASE_CREDENTIALS=firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id-from-console
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com

# JWT Secrets (Generate new secure keys)
SECRET_KEY=your-random-secret-key-min-32-chars
JWT_SECRET_KEY=your-random-jwt-secret-key-min-32-chars

# System Settings
DEFAULT_ATTENDANCE_RADIUS=100
MAX_ATTENDANCE_RADIUS=500
GEOLOCATION_ENABLED=True

# Admin Account
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=SecurePassword@123456

# CORS (Update with your domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Session Security (Production)
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict
```

## Step 6: Create Firestore Security Rules

1. In Firebase Console, go to **Firestore Database**
2. Click **"Rules"** tab
3. Replace with production rules:

```firestore
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function isAdmin() {
      return isAuthenticated() && 
             get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'ADMIN';
    }
    
    function isTeacher() {
      return isAuthenticated() && 
             get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'TEACHER';
    }
    
    function isStudent() {
      return isAuthenticated() && 
             get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'STUDENT';
    }
    
    // Users collection
    match /users/{userId} {
      allow read: if isAuthenticated() && (request.auth.uid == userId || isAdmin());
      allow write: if isAdmin();
      allow create: if isAdmin();
    }
    
    // Classes collection
    match /classes/{classId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin() || isTeacher();
    }
    
    // Enrollments collection
    match /enrollments/{enrollmentId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin();
    }
    
    // Attendance collection
    match /attendance/{attendanceId} {
      allow read: if isAuthenticated() && 
                     (resource.data.user_id == request.auth.uid || isAdmin() || isTeacher());
      allow create: if isStudent();
      allow update: if isAdmin();
      allow delete: if isAdmin();
    }
    
    // Devices collection
    match /devices/{deviceId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin();
    }
    
    // Audit logs collection
    match /audit_logs/{logId} {
      allow read: if isAdmin();
      allow write: if isAuthenticated();
    }
    
    // Blocked IPs collection
    match /blocked_ips/{ipId} {
      allow read: if isAdmin();
      allow write: if isAdmin();
    }
    
    // System settings collection
    match /system_settings/{settingId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin();
    }
  }
}
```

4. Click **"Publish"**

## Step 7: Create Cloud Storage Security Rules

1. In Firebase Console, go to **Storage**
2. Click **"Rules"** tab
3. Replace with production rules:

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    
    // Allow authenticated users to upload and download their own files
    match /uploads/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
                      request.resource.size < 16 * 1024 * 1024; // 16MB max
    }
    
    // Admin only
    match /admin/{allPaths=**} {
      allow read, write: if request.auth.token.role == 'ADMIN';
    }
  }
}
```

4. Click **"Publish"**

## Step 8: Initialize Firestore Database

1. Navigate to backend folder:
```bash
cd backend
```

2. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Run bootstrap script:
```bash
python -m bootstrap_firestore
```

Expected output:
```
🔥 Bootstrapping Firestore...

📝 Creating default admin user...
✅ Admin user created: [user-id]

⚙️  Initializing system settings...
✅ Setting 'attendance_radius' = 100
✅ Setting 'max_login_attempts' = 5
✅ Setting 'account_lock_duration' = 900
✅ Setting 'ip_block_duration' = 3600
✅ Setting 'auto_attendance_timeout' = 300
✅ Setting 'late_marking_minutes' = 15

📚 Initializing collections...
✅ Collection 'users' ready
✅ Collection 'classes' ready
✅ Collection 'enrollments' ready
✅ Collection 'attendance' ready
✅ Collection 'devices' ready
✅ Collection 'audit_logs' ready
✅ Collection 'blocked_ips' ready

✅ Bootstrap complete!
```

## Step 9: Enable Firebase Authentication (Optional for future)

For future email/password authentication:
1. Go to **Authentication** in Firebase
2. Click **"Get started"**
3. Click **"Email/Password"**
4. Toggle **"Enable"**

## Step 10: Set Up Firestore Indexes for Performance

Go to Firestore Database → Indexes and create these composite indexes:

```
Collection: attendance
Fields: user_id (Ascending), class_id (Ascending), created_at (Descending)

Collection: audit_logs
Fields: user_id (Ascending), created_at (Descending)

Collection: blocked_ips
Fields: ip_address (Ascending), is_blocked (Ascending)
```

## Step 11: Configure CORS for Frontend

Update your `.env`:
```dotenv
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,http://localhost:3000
```

## Step 12: Verify Deployment Readiness

1. Check `.env` file is in `.gitignore`
2. Check `firebase-credentials.json` is in `.gitignore`
3. Verify all required dependencies in `requirements.txt`:
```bash
pip freeze > requirements.txt
```

4. Test API endpoint:
```bash
python app.py
# In another terminal
curl http://localhost:5000/api/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2025-12-18T10:30:00Z"}
```

## Step 13: Deploy Backend

### Option A: Deploy to Google Cloud Run

```bash
# 1. Install Google Cloud SDK
# Download from https://cloud.google.com/sdk/docs/install

# 2. Authenticate
gcloud auth login
gcloud config set project your-project-id

# 3. Create .dockerignore
cat > .dockerignore <<EOF
venv
__pycache__
.env
*.pyc
.git
.gitignore
.pytest_cache
EOF

# 4. Create Dockerfile
cat > Dockerfile <<EOF
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE $PORT

CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "3", "--timeout", "60", "app:app"]
EOF

# 5. Deploy
gcloud run deploy geo-attendance-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars="FIREBASE_PROJECT_ID=your-project-id" \
  --memory 512Mi \
  --timeout 60
```

### Option B: Deploy to Heroku

```bash
# 1. Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create geo-attendance-api

# 4. Set environment variables
heroku config:set FIREBASE_PROJECT_ID=your-project-id
heroku config:set FIREBASE_CREDENTIALS=./firebase-credentials.json
heroku config:set JWT_SECRET_KEY=your-secret-key

# 5. Deploy
git push heroku main
```

## Step 14: Deploy Frontend

Update `frontend/.env.production`:
```env
VITE_API_URL=https://your-api-domain.com/api
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

Deploy to hosting service (Vercel, Netlify, etc.)

## Step 15: Monitor and Maintain

### Firebase Console Monitoring
- Check **Firestore → Database** for document count and storage
- Review **Storage → Files** for uploaded files
- Monitor **Logs** for errors

### Backend Monitoring
- Set up application logging
- Monitor API performance
- Track error rates

### Regular Maintenance
- Backup data regularly
- Review and update security rules
- Monitor and clean old audit logs
- Update dependencies

## Troubleshooting

### Firebase Connection Issues
```bash
# Test Firebase credentials
python -c "from firebase_client import get_db; print(get_db().collection('system_settings').limit(1).stream())"
```

### Missing Collections
Run bootstrap again:
```bash
python bootstrap_firestore.py
```

### Performance Issues
- Create composite indexes (see Step 10)
- Enable caching in frontend
- Optimize query limits

## Security Checklist

- [ ] `.env` file in `.gitignore`
- [ ] `firebase-credentials.json` in `.gitignore`
- [ ] Updated Firestore security rules
- [ ] Updated Cloud Storage security rules
- [ ] Changed default admin password
- [ ] Enabled HTTPS only
- [ ] Set secure JWT secrets (min 32 characters)
- [ ] Enabled CORS only for your domain
- [ ] Reviewed audit logs regularly
- [ ] Set up email notifications for alerts

## Next Steps

1. Deploy and test all API endpoints
2. Load test the system
3. Set up monitoring and alerts
4. Document your deployment
5. Train users on the system
