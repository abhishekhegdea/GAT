# Firebase Deployment - Quick Reference Card

**Status**: ✅ PRODUCTION READY | **Date**: Dec 18, 2025

---

## 🚀 5-Minute Quick Start

```bash
# 1. Set up environment
cd backend
cp .env.example .env
# Edit .env with your Firebase details

# 2. Verify setup
python setup-check.py

# 3. Initialize database
pip install -r requirements-prod.txt
python bootstrap_firestore.py

# 4. Test locally
python app.py
# In another terminal:
curl http://localhost:5000/api/health

# 5. Deploy
./deploy-cloud-run.sh your-project-id geo-attendance-api
```

---

## 📋 Essential Files

| File | Purpose |
|------|---------|
| `.env` | Configuration (create from .env.example) |
| `firebase-credentials.json` | Firebase service account |
| `requirements-prod.txt` | Python packages |
| `Dockerfile` | Container build |
| `bootstrap_firestore.py` | Database initialization |
| `deploy-cloud-run.sh` | Cloud Run deployment |
| `deploy-heroku.sh` | Heroku deployment |
| `setup-check.py` | Setup verification |

---

## 🔧 Environment Variables

```dotenv
# Firebase (REQUIRED)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_CREDENTIALS=firebase-credentials.json

# Security (REQUIRED)
SECRET_KEY=<generate-strong-32-char-key>
JWT_SECRET_KEY=<generate-strong-32-char-key>

# System (OPTIONAL)
CORS_ORIGINS=https://yourdomain.com
DEFAULT_ATTENDANCE_RADIUS=100
GEOLOCATION_ENABLED=True
```

---

## 💾 Firestore Collections (8)

```
1. users              → Admin, teacher, student accounts
2. classes           → Course information
3. enrollments       → Student enrollments
4. attendance        → Attendance marks + GPS location
5. devices           → Device registration
6. audit_logs        → Activity logging
7. blocked_ips       → IP blacklist
8. system_settings   → Configuration (6 settings)
```

---

## 🔐 Security Checklist

- [ ] `.env` in `.gitignore`
- [ ] `firebase-credentials.json` in `.gitignore`
- [ ] Strong SECRET_KEY (32+ chars)
- [ ] Strong JWT_SECRET_KEY (32+ chars)
- [ ] CORS restricted to your domain
- [ ] SESSION_COOKIE_SECURE=True
- [ ] SESSION_COOKIE_SAMESITE=Strict
- [ ] Default admin password changed
- [ ] Firestore security rules published
- [ ] Cloud Storage security rules published

---

## 🚀 Deployment Options

### Option 1: Google Cloud Run (⭐ Recommended)
```bash
chmod +x deploy-cloud-run.sh
./deploy-cloud-run.sh your-project-id geo-attendance-api us-central1
```
**Best for**: Auto-scaling, Firebase integration, free tier

### Option 2: Heroku
```bash
chmod +x deploy-heroku.sh
./deploy-heroku.sh geo-attendance-api
```
**Best for**: Simple deployments, good free tier

### Option 3: Docker
```bash
docker build -t geo-attendance-api:latest .
docker run -p 8080:8080 \
  -e FIREBASE_PROJECT_ID=your-id \
  geo-attendance-api:latest
```
**Best for**: Full control, multi-cloud

---

## 🧪 Testing Commands

```bash
# Health check
curl http://localhost:5000/api/health

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@system.com","password":"Admin@123"}'

# Mark attendance (with token)
curl -X POST http://localhost:5000/api/attendance/mark \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "class_id=class123" \
  -F "latitude=40.7128" \
  -F "longitude=-74.0060"
```

---

## 📊 API Endpoints

### Auth
```
POST   /api/auth/login
POST   /api/auth/refresh
POST   /api/auth/logout
```

### Student
```
GET    /api/student/profile
GET    /api/student/classes
POST   /api/attendance/mark
GET    /api/attendance/my-records
```

### Teacher
```
GET    /api/teacher/classes
GET    /api/teacher/attendance/{class_id}
POST   /api/classes
PUT    /api/classes/{class_id}
```

### Admin
```
GET    /api/admin/users
POST   /api/admin/users
GET    /api/admin/attendance
GET    /api/admin/audit-logs
```

---

## 📚 Documentation Map

```
START → SETUP_COMPLETE_SUMMARY.md (overview)
  ↓
  → DEPLOYMENT_READY.md (5-min guide)
  ↓
  → FIREBASE_DEPLOYMENT_SETUP.md (complete 15-step guide)
  ↓
  → PRE_DEPLOYMENT_CHECKLIST.md (verify everything)
  ↓
  → Deploy & Monitor
```

---

## 🔍 Verification Checklist

Run before deployment:
```bash
# Check setup
python setup-check.py

# Should show:
✅ Firebase Credentials
✅ Environment Configuration  
✅ Python Dependencies
✅ Firebase Connection
✅ Git Security
```

---

## ⚠️ Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Firebase connection fails | Check PROJECT_ID and credentials path |
| CORS errors | Update CORS_ORIGINS in .env |
| 401 errors | Verify JWT_SECRET_KEY is consistent |
| Collections missing | Run `python bootstrap_firestore.py` |
| Slow queries | Create composite Firestore indexes |
| Deployment timeout | Increase timeout in docker/heroku settings |

---

## 📞 Support Files

- **Overview**: SETUP_COMPLETE_SUMMARY.md
- **Quick Start**: DEPLOYMENT_READY.md
- **Step-by-Step**: FIREBASE_DEPLOYMENT_SETUP.md
- **Checklist**: PRE_DEPLOYMENT_CHECKLIST.md
- **Index**: DEPLOYMENT_DOCUMENTATION_INDEX.md
- **API Docs**: API.md
- **Architecture**: BACKEND_ARCHITECTURE.md

---

## 🎯 Next Steps

1. **Read**: SETUP_COMPLETE_SUMMARY.md (5 min)
2. **Prepare**: Firebase project + service account JSON
3. **Configure**: Create and edit .env file
4. **Verify**: Run setup-check.py
5. **Initialize**: Run bootstrap_firestore.py
6. **Deploy**: Run deploy-cloud-run.sh or deploy-heroku.sh
7. **Monitor**: Open Firebase Console
8. **Configure Frontend**: Update API URL in frontend .env

---

## 💡 Pro Tips

✅ Save Firebase project ID in a safe place
✅ Backup service account JSON (keep secure)
✅ Use strong, unique secrets for SECRET_KEY and JWT_SECRET_KEY
✅ Test locally before deploying
✅ Monitor logs after deployment
✅ Set up Firebase backups
✅ Review audit logs weekly
✅ Update dependencies monthly

---

## 🎉 Deployment Outcome

After successful deployment:

✅ Backend API running on Cloud Run / Heroku / Docker
✅ Firestore database with 8 collections ready
✅ 6 system settings configured
✅ JWT authentication enabled
✅ Security rules active
✅ Audit logging operational
✅ Ready for frontend integration
✅ Production monitoring in place

---

**Status**: ✅ READY FOR PRODUCTION
**Face Recognition**: ❌ Removed
**Time to Deploy**: 30-45 minutes
**Estimated Cost**: $0 (free tier) to $10/month (low usage)

---

**Questions?** See DEPLOYMENT_DOCUMENTATION_INDEX.md for full reference
