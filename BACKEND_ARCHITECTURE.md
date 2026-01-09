# Firestore Backend - Architecture Reference

## Project Structure

```
Geo-location/
├── backend/
│   ├── app.py                          ✅ Flask app with Firebase init
│   ├── firebase_client.py              ✅ Firebase initialization (NEW)
│   ├── bootstrap_firestore.py          ✅ Database bootstrap script (NEW)
│   ├── config.py                       ✅ Configuration (unchanged)
│   ├── requirements.txt                ✅ Updated with firebase-admin
│   ├── middleware/
│   │   └── auth.py                     ✅ JWT + role-based auth (Firestore)
│   ├── routes/
│   │   ├── auth.py                     ✅ Login/register/tokens (Firestore)
│   │   ├── admin.py                    ✅ Admin operations (Firestore)
│   │   ├── teacher.py                  ✅ Class management (Firestore)
│   │   ├── student.py                  ✅ Profile/attendance (Firestore)
│   │   ├── attendance.py               ✅ Mark attendance (Firestore)
│   │   └── classes.py                  ✅ Public listing (Firestore)
│   ├── services/
│   │   ├── firestore_auth.py           ✅ Auth DAL (NEW)
│   │   ├── firestore_users.py          ✅ User DAL (NEW)
│   │   ├── firestore_classes.py        ✅ Class DAL (NEW)
│   │   ├── firestore_attendance.py     ✅ Attendance DAL (NEW)
│   │   └── firestore_devices.py        ✅ Device/Settings/IP DAL (NEW)
│   └── utils/
│       ├── face_recognition_utils.py   ✅ Face processing
│       ├── geolocation.py              ✅ Location verification
│       ├── helpers.py                  ✅ Utility functions
│       └── (existing utilities)
│
├── frontend/                           ✅ Unchanged, ready for Firebase
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── README.md                           ✅ Updated for Firebase
├── DEPLOYMENT.md                       ✅ PostgreSQL deployment (legacy)
├── DEPLOYMENT_FIREBASE.md              ✅ Firebase deployment guide (NEW)
├── FIRESTORE_CONVERSION_SUMMARY.md     ✅ This conversion summary (NEW)
├── API.md                              ✅ API documentation
├── setup.sh                            ✅ Updated for Firebase
├── setup.bat                           ✅ Updated for Firebase
└── .env.example                        ✅ Updated for Firebase
```

## Data Access Layer (DAL) Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    API Routes                            │
│  (auth.py, admin.py, teacher.py, student.py, etc)      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│               Data Access Layer (Services)               │
├─────────────────────────────────────────────────────────┤
│  firestore_auth.py      → User authentication           │
│  firestore_users.py     → User management               │
│  firestore_classes.py   → Classes & enrollments         │
│  firestore_attendance.py → Attendance records           │
│  firestore_devices.py   → Devices, faces, settings      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              Firebase Client Layer                       │
├─────────────────────────────────────────────────────────┤
│  firebase_client.py → Singleton Firebase app            │
│    ├─ get_firebase_app()  → Firebase app instance       │
│    ├─ get_db()            → Firestore database          │
│    └─ get_bucket()        → Cloud Storage bucket        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Firebase Services   │
        ├──────────────────────┤
        │  Firestore Database  │
        │  Cloud Storage       │
        │  Cloud Authentication│
        └──────────────────────┘
```

## Key Functions by Module

### firestore_auth.py (Authentication DAL)
```
• get_user_by_email()      → Look up user by email
• get_user_by_id()         → Look up user by ID
• create_user()            → Create new user with hashed password
• verify_password()        → Verify password against hash
• update_login_failure()   → Track failed login attempts, lock account
• reset_login_attempts()   → Clear failed attempt counter
• update_last_login()      → Update last login timestamp
• upsert_device()          → Store/update device fingerprint
• log_audit()              → Log activity to audit_logs
• check_ip_blocked()       → Check if IP is blocked
• change_password()        → Change user password
• _utcnow()                → Get current UTC time
```

### firestore_users.py (User Management DAL)
```
• list_users()             → List users with filters/pagination
• get_user_by_id()         → Get user by ID
• get_user_by_email()      → Get user by email
• create_user()            → Create new user
• update_user()            → Update user fields
• deactivate_user()        → Mark user inactive
• activate_user()          → Mark user active
• lock_user()              → Lock user account (with duration)
• unlock_user()            → Unlock user account
• reset_password()         → Reset user password
• reset_face()             → Delete user's face encodings
• delete_user()            → Delete user (with cascading deletes)
```

### firestore_classes.py (Class Management DAL)
```
• create_class()           → Create new class
• get_class_by_id()        → Get class by ID
• list_classes()           → List classes (with teacher/active filters)
• update_class()           → Update class fields
• delete_class()           → Delete class (cascades enrollments)
• enroll_student()         → Enroll student in class
• get_enrollment_by_id()   → Get enrollment record
• list_enrollments_for_class()  → Get all students in class
• list_enrollments_for_student() → Get student's classes
• remove_enrollment()      → Remove student from class
• is_student_enrolled()    → Check if student is in class
```

### firestore_attendance.py (Attendance DAL)
```
• create_attendance()      → Create attendance record
• get_attendance_by_id()   → Get attendance by ID
• list_attendance()        → List with class/student/date filters
• update_attendance()      → Update attendance record
• lock_attendance()        → Lock attendance from editing
• delete_attendance()      → Delete attendance record
• check_duplicate_attendance() → Prevent double-marking today
• get_attendance_stats()   → Calculate statistics (present/late/absent)
```

### firestore_devices.py (Devices/Settings/IPs DAL)
```
DEVICE FUNCTIONS:
• list_devices()           → List user devices
• get_device_by_id()       → Get device details
• block_device()           → Block device
• unblock_device()         → Unblock device

FACE ENCODING FUNCTIONS:
• store_face_encoding()    → Store face encoding (auto-deletes old)
• get_face_encoding_by_user() → Get active face encoding for user
• get_face_encoding_by_id() → Get face encoding by ID
• delete_face_encoding()   → Delete/deactivate face encoding

SETTINGS FUNCTIONS:
• get_setting()            → Get system setting value
• get_all_settings()       → Get all settings as dict
• set_setting()            → Create/update setting

IP BLOCKING FUNCTIONS:
• list_blocked_ips()       → List active blocked IPs
• block_ip()               → Block IP address
• get_blocked_ip_by_id()   → Get blocked IP details
• unblock_ip()             → Unblock IP address
• check_ip_expired()       → Auto-deactivate expired blocks
```

## Firestore Collections Schema

### USERS Collection
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "password_hash": "$2b$12$...",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "role": "STUDENT",
  "is_active": true,
  "is_locked": false,
  "lock_until": null,
  "login_failures": 0,
  "last_login": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T08:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### CLASSES Collection
```json
{
  "id": "class_456",
  "teacher_id": "user_123",
  "name": "Advanced Python Programming",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "radius": 100,
  "start_time": "09:00",
  "end_time": "11:00",
  "schedule": "DAILY",
  "description": "Advanced Python concepts",
  "is_active": true,
  "created_at": "2024-01-01T08:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### ENROLLMENTS Collection
```json
{
  "id": "class_456_user_789",
  "class_id": "class_456",
  "student_id": "user_789",
  "enrolled_date": "2024-01-05T14:30:00Z",
  "is_active": true
}
```

### ATTENDANCE Collection
```json
{
  "id": "attend_001",
  "student_id": "user_789",
  "class_id": "class_456",
  "latitude": 40.7125,
  "longitude": -74.0061,
  "distance": 45.2,
  "face_match_score": 0.95,
  "status": "PRESENT",
  "is_valid": true,
  "is_locked": false,
  "ip_address": "192.168.1.100",
  "timestamp": "2024-01-15T09:05:00Z",
  "created_at": "2024-01-15T09:05:00Z",
  "updated_at": "2024-01-15T09:05:00Z"
}
```

### DEVICES Collection
```json
{
  "id": "device_001",
  "user_id": "user_789",
  "device_fingerprint": "abc123def456...",
  "device_name": "Chrome on Windows 10",
  "last_used": "2024-01-15T10:30:00Z",
  "is_blocked": false,
  "created_at": "2024-01-05T14:30:00Z"
}
```

### AUDIT_LOGS Collection
```json
{
  "id": "log_001",
  "user_id": "user_789",
  "action": "attendance_marked",
  "entity_type": "attendance",
  "entity_id": "attend_001",
  "details": {
    "class_id": "class_456",
    "status": "PRESENT",
    "distance": 45.2,
    "face_match": 0.95
  },
  "ip_address": "192.168.1.100",
  "timestamp": "2024-01-15T09:05:00Z"
}
```

### BLOCKED_IPS Collection
```json
{
  "id": "block_001",
  "ip_address": "203.0.113.45",
  "reason": "Multiple failed login attempts",
  "blocked_until": "2024-01-15T11:30:00Z",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### SYSTEM_SETTINGS Collection
```json
{
  "key": "attendance_radius",
  "value": 100,
  "type": "int",
  "updated_at": "2024-01-01T08:00:00Z"
}
```

## API Endpoint Summary

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| **AUTH ROUTES** |||
| POST | /api/auth/register | None | Register new user |
| POST | /api/auth/login | None | User login |
| POST | /api/auth/refresh | JWT | Refresh token |
| POST | /api/auth/logout | JWT | User logout |
| GET | /api/auth/me | JWT | Get current user |
| POST | /api/auth/change-password | JWT | Change password |
| **ADMIN ROUTES** |||
| GET | /api/admin/users | ADMIN | List users |
| POST | /api/admin/users | ADMIN | Create user |
| PUT | /api/admin/users/{id} | ADMIN | Update user |
| DELETE | /api/admin/users/{id} | ADMIN | Delete user |
| POST | /api/admin/users/{id}/deactivate | ADMIN | Deactivate user |
| POST | /api/admin/users/{id}/activate | ADMIN | Activate user |
| POST | /api/admin/users/{id}/lock | ADMIN | Lock user |
| POST | /api/admin/users/{id}/unlock | ADMIN | Unlock user |
| POST | /api/admin/users/{id}/reset-password | ADMIN | Reset password |
| POST | /api/admin/users/{id}/reset-face | ADMIN | Reset face |
| GET | /api/admin/settings | ADMIN | List settings |
| PUT | /api/admin/settings/{key} | ADMIN | Update setting |
| GET | /api/admin/attendance | ADMIN | List attendance |
| PUT | /api/admin/attendance/{id} | ADMIN | Update attendance |
| DELETE | /api/admin/attendance/{id} | ADMIN | Delete attendance |
| GET | /api/admin/devices | ADMIN | List devices |
| POST | /api/admin/devices/{id}/block | ADMIN | Block device |
| GET | /api/admin/blocked-ips | ADMIN | List blocked IPs |
| POST | /api/admin/blocked-ips | ADMIN | Block IP |
| DELETE | /api/admin/blocked-ips/{id} | ADMIN | Unblock IP |
| GET | /api/admin/statistics | ADMIN | Get statistics |
| **TEACHER ROUTES** |||
| GET | /api/teacher/classes | TEACHER | List classes |
| POST | /api/teacher/classes | TEACHER | Create class |
| GET | /api/teacher/classes/{id} | TEACHER | Get class details |
| PUT | /api/teacher/classes/{id} | TEACHER | Update class |
| DELETE | /api/teacher/classes/{id} | TEACHER | Delete class |
| GET | /api/teacher/classes/{id}/students | TEACHER | List students |
| POST | /api/teacher/classes/{id}/students | TEACHER | Enroll student |
| DELETE | /api/teacher/classes/{id}/students/{sid} | TEACHER | Remove student |
| GET | /api/teacher/classes/{id}/attendance | TEACHER | View attendance |
| PUT | /api/teacher/attendance/{id} | TEACHER | Edit attendance |
| **STUDENT ROUTES** |||
| GET | /api/student/profile | STUDENT | Get profile |
| POST | /api/student/register-face | STUDENT | Register face |
| GET | /api/student/classes | STUDENT | List enrolled classes |
| GET | /api/student/attendance/history | STUDENT | Attendance history |
| GET | /api/student/attendance/statistics | STUDENT | Attendance statistics |
| **ATTENDANCE ROUTES** |||
| POST | /api/attendance/mark | STUDENT | Mark attendance |
| POST | /api/attendance/validate-location | STUDENT | Validate location |
| GET | /api/attendance/check-eligibility/{cid} | STUDENT | Check eligibility |
| **PUBLIC ROUTES** |||
| GET | /api/classes | None | List classes |
| GET | /api/health | None | Health check |

## Deployment Checklist

- [x] Firebase Firestore configured (Native mode)
- [x] Cloud Storage bucket created
- [x] Service account credentials generated
- [x] All DAL modules created and tested
- [x] All route handlers converted to Firestore
- [x] Middleware updated for Firestore queries
- [x] Bootstrap script created
- [x] Environment configuration updated
- [x] Dependencies updated (firebase-admin added)
- [x] Documentation created (DEPLOYMENT_FIREBASE.md)
- [ ] Integration testing against live Firestore
- [ ] Security rules configured in Firebase console
- [ ] CORS properly configured for production domain
- [ ] Rate limiting implemented (optional)
- [ ] Monitoring and alerts set up (optional)
- [ ] Backup strategy defined
- [ ] Disaster recovery tested

## Performance Optimization Tips

1. **Indexing**: Firestore auto-creates necessary indexes for common queries
2. **Pagination**: All list endpoints support pagination (page/per_page params)
3. **Caching**: Use @lru_cache in firebase_client for Firebase app singleton
4. **Batch Operations**: Use batch writes for multiple updates
5. **Query Optimization**: DAL functions use WHERE filters efficiently

## Security Features Implemented

- ✅ Password hashing with bcrypt
- ✅ JWT token-based authentication
- ✅ Role-based access control (ADMIN/TEACHER/STUDENT)
- ✅ Account lockout after N failed login attempts
- ✅ IP address blocking with auto-expiration
- ✅ Device fingerprinting for anomaly detection
- ✅ Audit logging for all actions
- ✅ Face recognition verification for attendance
- ✅ Geolocation verification (GPS radius checking)
- ✅ CORS restriction by origin
- ✅ Sensitive data not returned in API responses

## Testing Commands

```bash
# Bootstrap Firestore
cd backend
python bootstrap_firestore.py

# Run development server
python app.py

# Test admin login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@system.com","password":"Admin@123"}'

# List users (requires token)
curl -H "Authorization: Bearer TOKEN_HERE" \
  http://localhost:5000/api/admin/users
```

## Next Steps

1. Configure Firebase Firestore security rules
2. Set up Cloud Monitoring and logging
3. Deploy frontend to Firebase Hosting
4. Deploy backend to Cloud Run or Compute Engine
5. Configure custom domain and SSL
6. Set up automated backups
7. Create monitoring dashboards
8. Document runbooks for operations team
