# Firebase Backend - Quick Reference Guide

## 🚀 Quick Start (5 minutes)

### 1. Get Firebase Credentials
```bash
# Go to: https://console.firebase.google.com
# 1. Create new project or select existing
# 2. Enable Firestore Database (Native mode)
# 3. Enable Cloud Storage
# 4. Project Settings → Service Accounts → Generate Key (JSON)
# 5. Save file as: backend/service-account-key.json
```

### 2. Configure Environment
```bash
cd backend
cat > .env << EOF
FIREBASE_CREDENTIALS=$(pwd)/service-account-key.json
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-key
CORS_ORIGINS=http://localhost:3000
EOF
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python bootstrap_firestore.py
```

### 5. Run Backend
```bash
python app.py
# Runs on http://localhost:5000
```

### 6. Test Health
```bash
curl http://localhost:5000/api/health
```

## 📚 Common Commands

### Start Backend
```bash
cd backend && python app.py
```

### Bootstrap Firestore
```bash
cd backend && python bootstrap_firestore.py
```

### Run with Gunicorn (Production)
```bash
cd backend && gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
```

### View Logs
```bash
gcloud firestore-logs list --limit 10
```

## 🔑 Default Credentials

After bootstrap_firestore.py:
```
Admin Email: admin@system.com
Admin Password: Admin@123

Teacher Email: teacher@test.com
Teacher Password: Teacher@123

Student Email: student@test.com
Student Password: Student@123
```

## 🎯 Key Endpoints

### Authentication
```bash
# Register
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass@123",
  "first_name": "John",
  "last_name": "Doe"
}

# Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass@123"
}

# Refresh Token
POST /api/auth/refresh
# (requires JWT in Authorization header)

# Get Current User
GET /api/auth/me
# (requires JWT in Authorization header)
```

### Admin Operations
```bash
# List all users
GET /api/admin/users?page=1&per_page=20

# Create user
POST /api/admin/users
{
  "email": "newuser@example.com",
  "password": "NewPass@123",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "STUDENT"
}

# Get system statistics
GET /api/admin/statistics
```

### Teacher Operations
```bash
# List teacher's classes
GET /api/teacher/classes

# Create class
POST /api/teacher/classes
{
  "name": "Python 101",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "radius": 100,
  "start_time": "09:00",
  "end_time": "11:00"
}

# View class attendance
GET /api/teacher/classes/{class_id}/attendance
```

### Student Operations
```bash
# Get profile
GET /api/student/profile

# Register face
POST /api/student/register-face
# (multipart form with 'image' file)

# Mark attendance
POST /api/attendance/mark
{
  "class_id": "class_123",
  "latitude": 40.7125,
  "longitude": -74.0061,
  "image": <file>  # Optional, required for face verification
}

# Check attendance eligibility
GET /api/attendance/check-eligibility/class_123
```

## 🔐 Authentication Headers

All protected endpoints require JWT in Authorization header:
```bash
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

Example with curl:
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  http://localhost:5000/api/admin/users
```

## 📊 Firestore Collections

| Collection | Purpose | Documents |
|------------|---------|-----------|
| users | User accounts | One per user |
| classes | Classes | One per class |
| enrollments | Student-class links | One per enrollment |
| attendance | Attendance records | One per marking |
| face_encodings | Face biometrics | One active per student |
| devices | Registered devices | One per device |
| audit_logs | Activity logs | All actions |
| blocked_ips | Blocked IPs | Active blocks |
| system_settings | Configuration | Settings keys |

## 🛡️ Common Settings

Edit in Firebase console or via API:

```bash
# Via API (requires admin token)
PUT /api/admin/settings/attendance_radius
{
  "value": 150  # meters
}

PUT /api/admin/settings/face_recognition_threshold
{
  "value": 0.7  # 0-1 scale
}

PUT /api/admin/settings/max_login_attempts
{
  "value": 5
}
```

## 🐛 Troubleshooting

### Firebase connection fails
```bash
# Check credentials file exists
ls backend/service-account-key.json

# Verify env variables
echo $FIREBASE_CREDENTIALS
echo $FIREBASE_PROJECT_ID
```

### Face recognition not working
```bash
# Check system settings
GET /api/admin/settings

# Default threshold is 0.6 (60% match)
# Lower value = more permissive matching
# Increase if too many false positives
```

### User can't login
```bash
# Check if user is active
GET /api/admin/users?search=email@example.com

# Check if account is locked
# If locked, admin can unlock:
POST /api/admin/users/{user_id}/unlock
```

### Attendance errors
```bash
# Verify student enrolled in class
GET /api/teacher/classes/{class_id}/students

# Check class location settings
GET /api/teacher/classes/{class_id}

# Check student has face registered
GET /api/student/profile
```

## 📦 Project Structure

```
backend/
├── app.py                 # Flask application
├── firebase_client.py     # Firebase initialization
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── bootstrap_firestore.py # Database setup
├── middleware/
│   └── auth.py          # JWT & roles
├── routes/
│   ├── auth.py          # Login/register
│   ├── admin.py         # Admin operations
│   ├── teacher.py       # Teacher operations
│   ├── student.py       # Student operations
│   ├── attendance.py    # Attendance marking
│   └── classes.py       # Public classes
├── services/
│   ├── firestore_auth.py
│   ├── firestore_users.py
│   ├── firestore_classes.py
│   ├── firestore_attendance.py
│   └── firestore_devices.py
└── utils/
    ├── face_recognition_utils.py
    ├── geolocation.py
    └── helpers.py
```

## 🚨 Important Notes

1. **Credentials**: Never commit `service-account-key.json` to git
2. **Passwords**: Change default passwords immediately in production
3. **CORS**: Update CORS_ORIGINS for production domain
4. **Backups**: Enable Firestore backups in Google Cloud
5. **Monitoring**: Set up Firebase monitoring and alerts
6. **Rate Limiting**: Implement rate limiting for API (optional)
7. **HTTPS**: Always use HTTPS in production
8. **Face Data**: Ensure compliance with data protection laws

## 📖 Additional Resources

- [Firebase Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Admin SDK](https://firebase.google.com/docs/database/admin/start)
- [Cloud Storage Documentation](https://firebase.google.com/docs/storage)
- [Security Rules Guide](https://firebase.google.com/docs/firestore/security/start)
- [Full Deployment Guide](./DEPLOYMENT_FIREBASE.md)
- [Architecture Reference](./BACKEND_ARCHITECTURE.md)

## 💡 Tips & Tricks

### View Firestore Data
```bash
# Via Firebase Console
# https://console.firebase.google.com → Firestore Database

# Via Firebase CLI
firebase firestore:shell
> db.collection('users').get()
```

### Export Data
```bash
gcloud firestore export gs://your-bucket/backups/backup-name
```

### View Logs
```bash
gcloud app logs read
```

### Reset Everything
```bash
# WARNING: Deletes all Firestore data!
# 1. Go to Firebase Console
# 2. Firestore Database → Start Collection
# 3. Delete collections manually
# 4. Run: python bootstrap_firestore.py
```

## 📱 Frontend Setup

If you have a frontend:

1. Install Firebase SDK:
   ```bash
   npm install firebase
   ```

2. Configure firebase.js:
   ```javascript
   import { initializeApp } from 'firebase/app';
   
   const config = {
     projectId: process.env.VITE_FIREBASE_PROJECT_ID,
     storageBucket: process.env.VITE_FIREBASE_STORAGE_BUCKET,
     // ... other config
   };
   
   const app = initializeApp(config);
   ```

3. Set API endpoint:
   ```javascript
   const API_BASE = process.env.VITE_API_BASE_URL || 'http://localhost:5000/api';
   ```

## ✅ Deployment Checklist

- [ ] Firebase project created
- [ ] Firestore (Native) enabled
- [ ] Cloud Storage enabled
- [ ] Service account created
- [ ] Environment configured (.env)
- [ ] Dependencies installed
- [ ] Bootstrap script run
- [ ] Backend starts without errors
- [ ] Health check endpoint responds
- [ ] Can login with default credentials
- [ ] CORS configured for frontend
- [ ] Frontend API endpoint updated
- [ ] Rate limiting configured (optional)
- [ ] Monitoring set up (optional)
- [ ] Backups configured (optional)

## 🎓 Learning Resources

- Study `BACKEND_ARCHITECTURE.md` for system design
- Review `DEPLOYMENT_FIREBASE.md` for deployment details
- Check DAL modules in `services/` for code patterns
- Explore `routes/` for endpoint implementations

## 📞 Support

For issues:
1. Check error logs: `python app.py`
2. Review Firebase console for data issues
3. Verify environment variables are set
4. Check Firestore security rules
5. Consult [Firebase documentation](https://firebase.google.com/docs)

---

**Ready to deploy?** See [DEPLOYMENT_FIREBASE.md](./DEPLOYMENT_FIREBASE.md) for full guide.
