# Firebase Backend Deployment Guide

This guide covers deploying the Geolocation-Based Attendance System with Firebase as the backend instead of PostgreSQL.

## Prerequisites

- Node.js 16+ (for Firebase Admin SDK)
- Python 3.8+
- Firebase project with:
  - Firestore Database (Native mode)
  - Cloud Storage
  - Service Account credentials

## Backend Setup

### 1. Firebase Project Setup

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project or select existing one
3. Enable Firestore Database:
   - Go to "Firestore Database"
   - Click "Create Database"
   - Choose "Start in Native mode"
   - Select your preferred region
4. Enable Cloud Storage:
   - Go to "Storage"
   - Click "Create bucket"
   - Use default settings
5. Create Service Account:
   - Go to "Project Settings" → "Service Accounts"
   - Click "Generate New Private Key"
   - Save the JSON file securely

### 2. Environment Configuration

Create `.env` file in `backend/` directory:

```env
# Firebase Configuration
FIREBASE_CREDENTIALS=/path/to/service-account-key.json
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_STORAGE_BUCKET=your-storage-bucket-name

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Logging
LOG_LEVEL=INFO
```

### 3. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Bootstrap Firestore

Initialize Firestore with default data:

```bash
python bootstrap_firestore.py
```

This will:
- Create default admin user (admin@system.com / Admin@123)
- Initialize system settings collection
- Create all required collections
- Add sample test users (optional)

### 5. Run Backend Server

Development:
```bash
python app.py
```

Production (with Gunicorn):
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
```

## Frontend Setup

Update `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:5000/api
VITE_FIREBASE_PROJECT_ID=your-firebase-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-storage-bucket-name
```

Install and run:
```bash
cd frontend
npm install
npm run dev
```

## Firestore Collections Schema

### users
```
{
  id: string (Firebase Auth UID or custom ID)
  email: string (unique)
  password_hash: string (bcrypt)
  first_name: string
  last_name: string
  role: enum (ADMIN|TEACHER|STUDENT)
  is_active: boolean
  is_locked: boolean
  lock_until: timestamp (optional)
  login_failures: int
  last_login: timestamp
  created_at: timestamp
  updated_at: timestamp
}
```

### classes
```
{
  id: string
  teacher_id: string (reference to users)
  name: string
  latitude: float
  longitude: float
  radius: int (meters)
  start_time: string (HH:MM)
  end_time: string (HH:MM)
  schedule: string (DAILY|WEEKLY|CUSTOM)
  description: string
  is_active: boolean
  created_at: timestamp
  updated_at: timestamp
}
```

### enrollments
```
{
  id: string (format: class_id_student_id)
  class_id: string (reference to classes)
  student_id: string (reference to users)
  enrolled_date: timestamp
  is_active: boolean
}
```

### attendance
```
{
  id: string
  student_id: string (reference to users)
  class_id: string (reference to classes)
  latitude: float
  longitude: float
  distance: float (meters)
  face_match_score: float (0-1)
  status: enum (PRESENT|LATE|ABSENT)
  is_valid: boolean
  is_locked: boolean
  ip_address: string
  timestamp: timestamp
  created_at: timestamp
  updated_at: timestamp
}
```

### face_encodings
```
{
  id: string
  user_id: string (reference to users)
  encoding: blob (pickle-serialized numpy array)
  image_path: string (path in Cloud Storage)
  is_active: boolean
  created_at: timestamp
  updated_at: timestamp
}
```

### devices
```
{
  id: string
  user_id: string (reference to users)
  device_fingerprint: string
  device_name: string
  last_used: timestamp
  is_blocked: boolean
  created_at: timestamp
}
```

### audit_logs
```
{
  id: string
  user_id: string
  action: string
  entity_type: string
  entity_id: string
  details: map
  ip_address: string
  timestamp: timestamp
}
```

### blocked_ips
```
{
  id: string
  ip_address: string
  reason: string
  blocked_until: timestamp
  is_active: boolean
  created_at: timestamp
}
```

### system_settings
```
Documents in this collection:
{
  key: string
  value: any
  type: string
  updated_at: timestamp
}

Common settings:
- attendance_radius: int (meters, default: 100)
- face_recognition_threshold: float (default: 0.6)
- max_login_attempts: int (default: 5)
- account_lock_duration: int (seconds, default: 900)
- ip_block_duration: int (seconds, default: 3600)
- auto_attendance_timeout: int (seconds, default: 300)
- late_marking_minutes: int (default: 15)
```

## Cloud Storage Structure

Face images are stored in Cloud Storage under:
```
faces/{user_id}.jpg
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - User logout
- `POST /api/auth/change-password` - Change password
- `GET /api/auth/me` - Get current user

### Admin (requires ADMIN role)
- `GET /api/admin/users` - List all users
- `POST /api/admin/users` - Create user
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user
- `POST /api/admin/users/{id}/lock` - Lock user account
- `POST /api/admin/users/{id}/unlock` - Unlock user account
- `GET /api/admin/settings` - Get all settings
- `PUT /api/admin/settings/{key}` - Update setting
- `GET /api/admin/attendance` - List attendance records
- `GET /api/admin/devices` - List devices
- `GET /api/admin/blocked-ips` - List blocked IPs
- `POST /api/admin/blocked-ips` - Block IP
- `DELETE /api/admin/blocked-ips/{id}` - Unblock IP
- `GET /api/admin/statistics` - Get system statistics

### Teacher (requires TEACHER role)
- `GET /api/teacher/classes` - List teacher's classes
- `POST /api/teacher/classes` - Create class
- `PUT /api/teacher/classes/{id}` - Update class
- `DELETE /api/teacher/classes/{id}` - Delete class
- `GET /api/teacher/classes/{id}/students` - List enrolled students
- `POST /api/teacher/classes/{id}/students` - Enroll student
- `DELETE /api/teacher/classes/{id}/students/{student_id}` - Remove student
- `GET /api/teacher/classes/{id}/attendance` - View class attendance

### Student (requires STUDENT role)
- `GET /api/student/profile` - Get student profile
- `POST /api/student/register-face` - Register face
- `GET /api/student/classes` - List enrolled classes
- `GET /api/student/attendance/history` - View attendance history
- `GET /api/student/attendance/statistics` - View attendance statistics

### Attendance
- `POST /api/attendance/mark` - Mark attendance
- `POST /api/attendance/validate-location` - Validate location
- `GET /api/attendance/check-eligibility/{class_id}` - Check eligibility

### Classes
- `GET /api/classes` - List all active classes

## Deployment on Cloud Platforms

### Google Cloud Run
```bash
gcloud run deploy geolocation-attendance \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_CREDENTIALS=/workspace/credentials.json
```

### Heroku
```bash
heroku create your-app-name
heroku config:set FIREBASE_CREDENTIALS=$(cat service-account-key.json)
heroku config:set FIREBASE_PROJECT_ID=your-project-id
git push heroku main
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ENV FLASK_APP=app.py

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app('production')"]
```

## Security Considerations

1. **Firestore Security Rules**: Configure security rules to restrict data access by role
2. **Service Account**: Never commit service account JSON file
3. **Environment Variables**: Use secure secret management (Google Secret Manager, Heroku Secrets)
4. **CORS**: Restrict CORS origins to your frontend domain
5. **Rate Limiting**: Implement rate limiting for authentication endpoints
6. **Face Data**: Encrypt face encodings in transit and at rest

## Monitoring and Logging

### Enable Firestore Monitoring
- Go to Cloud Monitoring console
- Set up alerts for quota usage and errors

### View Application Logs
```bash
gcloud functions logs read geolocation-attendance --limit 50
```

## Troubleshooting

### Firestore Connection Issues
```python
# Test Firebase connection
from firebase_client import get_db
db = get_db()
print(db.collection('users').limit(1).stream())
```

### Face Recognition Issues
- Ensure face encoding threshold is appropriate
- Check uploaded image quality
- Verify face_encodings collection has valid documents

### JWT Token Issues
- Verify JWT_SECRET_KEY is set
- Check token expiration settings in config.py

## Backup and Recovery

### Firestore Backups
```bash
gcloud firestore export gs://your-bucket/backups/backup-name
```

### Restore from Backup
```bash
gcloud firestore import gs://your-bucket/backups/backup-name
```

## Support

For issues with Firebase configuration, see [Firebase Documentation](https://firebase.google.com/docs)
For API issues, check logs: `docker logs container-id`
