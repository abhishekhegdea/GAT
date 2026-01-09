# 🔥 Firebase Setup Guide - Step by Step

## PART 1: Create Firebase Project

### Step 1.1: Go to Firebase Console
1. Open your browser and go to: **https://console.firebase.google.com**
2. Sign in with your Google account

### Step 1.2: Create a New Project
1. Click **"Create a project"** button
2. Enter project name: `glaad-app` (or your preferred name)
3. Click **"Continue"**
4. You can disable Google Analytics (not needed for this project)
5. Click **"Create project"**
6. Wait for project creation to complete

### Step 1.3: Note Your Project ID
- After creation, you'll see your project dashboard
- Your project ID will appear at the top or in URL: `https://console.firebase.google.com/project/YOUR_PROJECT_ID`
- **Note down your Project ID** (e.g., `glaad-app`)

---

## PART 2: Enable Firestore Database

### Step 2.1: Create Firestore Database
1. In left sidebar, click **"Firestore Database"**
2. Click **"Create database"** button
3. Select **"Start in Native mode"** (NOT Datastore mode!)
4. Choose location closest to you (e.g., us-central1)
5. Click **"Enable"** button
6. Wait for database to be created

### Step 2.2: Update Security Rules (Temporary - for development)
1. In Firestore console, click **"Rules"** tab
2. Replace the rules with:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow all reads and writes for development
    // IMPORTANT: Change this before production!
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```
3. Click **"Publish"**

**⚠️ WARNING**: This allows anyone to read/write data. Configure proper rules before production!

---

## PART 3: Enable Cloud Storage

### Step 3.1: Create Cloud Storage Bucket
1. In left sidebar, click **"Storage"**
2. Click **"Create bucket"** button
3. Bucket name: `your_project_id.appspot.com` (replace `your_project_id` with your actual project ID)
4. Choose location same as Firestore
5. Keep default settings and click **"Create"**
6. Wait for bucket to be created

### Step 3.2: Update Storage Rules (Temporary - for development)
1. Click **"Rules"** tab
2. Replace rules with:
```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Allow all reads and writes for development
    match /{allPaths=**} {
      allow read, write: if true;
    }
  }
}
```
3. Click **"Publish"**

**⚠️ WARNING**: This allows anyone to access files. Configure proper rules before production!

---

## PART 4: Create Service Account & Download Credentials

### Step 4.1: Go to Project Settings
1. Click the **gear icon** (⚙️) in top-right corner
2. Click **"Project settings"**

### Step 4.2: Create Service Account
1. Click **"Service Accounts"** tab
2. Click **"Generate New Private Key"** button
3. A JSON file will download automatically
4. **Important**: Save this file securely as `firebase-adminsdk.json` in your `backend/` folder
5. ⚠️ **NEVER commit this file to Git!** Add it to `.gitignore`

### Step 4.3: Note Your Credentials
From the downloaded JSON file, note:
- **project_id**: e.g., `glaad-app`
- **storage_bucket**: e.g., `glaad-app.appspot.com`

---

## PART 5: Create Firestore Collections & Fields

Now we'll create all 9 collections with their schema. Go to **Firestore Database** in console.

### Step 5.1: Create `users` Collection
1. Click **"Create collection"** button
2. Collection name: **`users`**
3. Click **"Next"**
4. Add first document:
   - Document ID: **`Auto ID`** (let it auto-generate)
   - Click **"Add field"** and add these fields:

| Field Name | Type | Value |
|-----------|------|-------|
| email | string | admin@system.com |
| first_name | string | System |
| last_name | string | Admin |
| role | string | ADMIN |
| is_active | boolean | true |
| is_locked | boolean | false |
| lock_until | timestamp | (leave empty) |
| login_failures | number | 0 |
| password_hash | string | $2b$12$... (we'll set this via script) |
| created_at | timestamp | (click "Server timestamp") |
| updated_at | timestamp | (click "Server timestamp") |

5. Click **"Save"**

### Step 5.2: Create `classes` Collection
1. Click **"Create collection"** button
2. Collection name: **`classes`**
3. Click **"Next"**
4. Add first document with these fields:

| Field Name | Type | Value |
|-----------|------|-------|
| name | string | Sample Class |
| teacher_id | string | (will be populated by app) |
| latitude | number | 40.7128 |
| longitude | number | -74.0060 |
| radius | number | 100 |
| start_time | string | 09:00 |
| end_time | string | 11:00 |
| schedule | string | DAILY |
| description | string | Sample class |
| is_active | boolean | true |
| created_at | timestamp | (click "Server timestamp") |
| updated_at | timestamp | (click "Server timestamp") |

5. Click **"Save"**

### Step 5.3: Create `enrollments` Collection
1. Click **"Create collection"** button
2. Collection name: **`enrollments`**
3. Click **"Next"**
4. For now just click **"Save"** (we'll populate this from the app)
   - Note: Document IDs should be: `{class_id}_{student_id}`
   - Fields: class_id, student_id, enrolled_date, is_active

### Step 5.4: Create `attendance` Collection
1. Click **"Create collection"** button
2. Collection name: **`attendance`**
3. Click **"Next"**
4. For now just click **"Save"** (we'll populate this from the app)
   - Fields: student_id, class_id, latitude, longitude, distance, face_match_score, status, is_valid, is_locked, ip_address, timestamp

### Step 5.5: Create `devices` Collection
1. Click **"Create collection"** button
2. Collection name: **`devices`**
3. Click **"Next"**
4. For now just click **"Save"**
   - Fields: user_id, device_fingerprint, device_name, last_used, is_blocked

### Step 5.6: Create `audit_logs` Collection
1. Click **"Create collection"** button
2. Collection name: **`audit_logs`**
3. Click **"Next"**
4. For now just click **"Save"**
   - Fields: user_id, action, entity_type, entity_id, details (map), ip_address, timestamp

### Step 5.7: Create `blocked_ips` Collection
1. Click **"Create collection"** button
2. Collection name: **`blocked_ips`**
3. Click **"Next"**
4. For now just click **"Save"**
   - Fields: ip_address, reason, blocked_until, is_active, created_at

### Step 5.8: Create `system_settings` Collection
1. Click **"Create collection"** button
2. Collection name: **`system_settings`**
3. Click **"Next"**
4. Add documents for each setting. First one:
   - Document ID: **`attendance_radius`**
   - Fields:
     - key: string = `attendance_radius`
     - value: number = `100`
     - type: string = `int`
     - updated_at: timestamp = (Server timestamp)
5. Click **"Save"**

6. Add more settings by clicking **"Add document"**:

**Setting 2: max_login_attempts**
```
key: max_login_attempts
value: 5
type: int
```

**Setting 3: account_lock_duration**
```
key: account_lock_duration
value: 900
type: int
```

**Setting 4: ip_block_duration**
```
key: ip_block_duration
value: 3600
type: int
```

**Setting 5: auto_attendance_timeout**
```
key: auto_attendance_timeout
value: 300
type: int
```

**Setting 6: late_marking_minutes**
```
key: late_marking_minutes
value: 15
type: int
```

---

## PART 6: Configure Your Local .env File

### Step 6.1: Create `.env` File
1. Navigate to your `backend/` folder
2. Create a new file named `.env` (note the dot at the beginning)
3. Add these contents, replacing with your actual values:

```dotenv
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production

# Firebase (Firestore/Storage)
FIREBASE_CREDENTIALS=/path/to/firebase-adminsdk.json
FIREBASE_PROJECT_ID=glaad-app
FIREBASE_STORAGE_BUCKET=glaad-app.appspot.com

# JWT Configuration
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# System Settings
DEFAULT_ATTENDANCE_RADIUS=100
MAX_ATTENDANCE_RADIUS=500
FACE_RECOGNITION_ENABLED=True
```

### Step 6.2: Update Paths
- Replace `/path/to/firebase-adminsdk.json` with the actual full path to your JSON file
  - Windows example: `D:/OneDrive/Desktop/Geo-location/backend/firebase-adminsdk.json`
  - Linux/Mac example: `/home/user/Geo-location/backend/firebase-adminsdk.json`
- Replace `glaad-app` with your actual Firebase Project ID (from Step 1.3)
- Replace `glaad-app.appspot.com` with your actual Storage Bucket name (from Step 3.2)

---

## PART 7: Verify Everything Works

### Step 7.1: Open Terminal
1. Open PowerShell or Command Prompt
2. Navigate to your backend folder:
   ```bash
   cd D:\OneDrive\Desktop\Geo-location\backend
   ```

### Step 7.2: Activate Virtual Environment
```bash
# On Windows:
.\venv\Scripts\Activate.ps1

# On Linux/Mac:
source venv/bin/activate
```

### Step 7.3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 7.4: Test Firebase Connection
```bash
python -c "from firebase_client import get_db; db = get_db(); print('✅ Firebase connected successfully!')"
```

You should see: **✅ Firebase connected successfully!**

If you get an error, check:
- Is the JSON file path correct in `.env`?
- Is the `FIREBASE_CREDENTIALS` variable set correctly?
- Is the JSON file in the right location?

### Step 7.5: Bootstrap Database
```bash
python bootstrap_firestore.py
```

You should see output like:
```
🔥 Bootstrapping Firestore...
📝 Creating default admin user...
✅ Admin user created: user_123
⚙️  Initializing system settings...
✅ Setting 'attendance_radius' = 100
...
🎉 Firestore bootstrap completed!
```

### Step 7.6: Start Backend
```bash
python app.py
```

Backend should start on `http://localhost:5000`

### Step 7.7: Test Health Endpoint
Open a **new terminal** and run:
```bash
curl http://localhost:5000/api/health
```

You should see:
```json
{
  "status": "healthy",
  "message": "Geolocation Attendance System API is running"
}
```

---

## PART 8: Test Login

### Step 8.1: Get Access Token
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@system.com","password":"Admin@123"}'
```

You should get a response with `access_token` and `refresh_token`.

### Step 8.2: Test Authenticated Endpoint
Replace `YOUR_TOKEN` with the token from Step 8.1:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/admin/users
```

You should see a list of users.

---

## 📋 Summary Checklist

- [ ] Created Firebase project
- [ ] Noted Project ID
- [ ] Enabled Firestore Database (Native mode)
- [ ] Enabled Cloud Storage
- [ ] Downloaded service account JSON
- [ ] Saved JSON in backend folder
- [ ] Created `.env` file
- [ ] Updated all `.env` values with correct paths
- [ ] Created 8 Firestore collections:
  - [ ] users
  - [ ] classes
  - [ ] enrollments
  - [ ] attendance
  - [ ] devices
  - [ ] audit_logs
  - [ ] blocked_ips
  - [ ] system_settings
- [ ] Added system settings (6 settings)
- [ ] Installed Python dependencies
- [ ] Tested Firebase connection
- [ ] Ran bootstrap script
- [ ] Started backend server
- [ ] Tested health endpoint
- [ ] Tested login endpoint

---

## 🆘 Troubleshooting

### Issue: "Permission denied" or "Unauthorized" error
**Solution**: 
- Check `.env` file has correct `FIREBASE_CREDENTIALS` path
- Verify JSON file exists at that path
- Make sure you're in development mode (security rules set to allow all)

### Issue: "Collection not found"
**Solution**:
- Make sure all 9 collections are created in Firestore
- Collection names are case-sensitive

### Issue: "Invalid service account"
**Solution**:
- Re-download the service account JSON from Firebase console
- Place it in backend folder
- Update `.env` with correct path

### Issue: Storage bucket not found
**Solution**:
- Go to Firebase Storage and create a bucket if not present
- Bucket name should be: `{project_id}.appspot.com`
- Update `FIREBASE_STORAGE_BUCKET` in `.env`

### Issue: Port 5000 already in use
**Solution**:
```bash
# Find what's using port 5000
netstat -ano | findstr :5000

# Or use a different port
python app.py --port 5001
```

---

## 🎉 You're All Set!

Once you complete these steps, your Firebase backend is ready to use. You can now:

1. ✅ Run the backend server
2. ✅ Login with default credentials
3. ✅ Create teachers and students
4. ✅ Create classes
5. ✅ Mark attendance
6. ✅ Use the admin dashboard

---

## 📞 Next Steps

1. **Connect Frontend**: Update frontend `.env` with Firebase config
2. **Test Endpoints**: Use the API endpoints to create test data
3. **Configure Security**: Set proper Firestore security rules for production
4. **Deploy**: Deploy to Google Cloud Run or your preferred platform

For more details, see:
- [DEPLOYMENT_FIREBASE.md](./DEPLOYMENT_FIREBASE.md)
- [QUICK_START_FIREBASE.md](./QUICK_START_FIREBASE.md)
- [BACKEND_ARCHITECTURE.md](./BACKEND_ARCHITECTURE.md)
