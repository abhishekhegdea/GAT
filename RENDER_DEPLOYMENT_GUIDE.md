# Step-by-Step Render Deployment

Follow these exact steps to deploy your backend for **FREE** on Render.

---

## Prerequisites

1. ✅ GitHub account
2. ✅ Firebase project with credentials
3. ✅ 15 minutes of your time

---

## Step 1: Push to GitHub (if not already)

```bash
# Open terminal in project root
cd d:\OneDrive\Desktop\Geo-location

# Initialize git (if not done)
git init

# Create .gitignore
echo "node_modules/
__pycache__/
*.pyc
.env
backend/.env
frontend/.env
frontend/dist/
backend/uploads/
.DS_Store
*.log" > .gitignore

# Add all files
git add .
git commit -m "Ready for deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR-USERNAME/geo-attendance.git
git push -u origin main
```

---

## Step 2: Sign Up for Render

1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with your **GitHub account**
4. Authorize Render to access your repositories

---

## Step 3: Create Web Service

1. Click **"New +"** (top right)
2. Select **"Web Service"**
3. Click **"Connect GitHub"** (if not connected)
4. Find your repository: `geo-attendance`
5. Click **"Connect"**

---

## Step 4: Configure Service

Fill in these settings:

### Basic Settings
- **Name**: `geo-attendance-api` (or any name you like)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

### Build Settings
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```

- **Start Command**:
  ```
  gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
  ```

### Instance Type
- Select **"Free"** (FREE $0/month)

---

## Step 5: Add Environment Variables

Scroll down to **"Environment Variables"** section and click **"Add Environment Variable"**.

Add these one by one:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `your-super-secret-key-change-this-12345` (generate random string) |
| `JWT_SECRET_KEY` | `your-jwt-secret-key-67890` (generate random string) |
| `CORS_ORIGINS` | `*` (allow all for now, change later) |
| `PORT` | `10000` (Render uses this) |

### Firebase Configuration

**Option A: Using JSON String (Recommended)**

1. Open your `backend/firebase-credentials.json` file
2. Copy the **entire JSON content**
3. Add environment variable:
   - **Key**: `FIREBASE_CREDENTIALS_JSON`
   - **Value**: Paste the entire JSON (Render handles multi-line)

**Option B: Using File (Alternative)**

If Option A doesn't work:
1. **Key**: `FIREBASE_PROJECT_ID`
   **Value**: Your project ID from Firebase (e.g., `geo-attendance-12345`)

2. You'll need to modify `backend/firebase_client.py` to read from env var instead of file.

---

## Step 6: Deploy!

1. Click **"Create Web Service"** (bottom of page)
2. Wait 3-5 minutes while Render:
   - Pulls your code from GitHub
   - Installs dependencies
   - Starts the server
3. Watch the **deployment logs** in real-time

---

## Step 7: Get Your Backend URL

Once deployment succeeds (green checkmark):

1. Look for the URL at the top: `https://geo-attendance-api.onrender.com`
2. **Copy this URL** - you'll need it for the frontend!
3. Test it by visiting: `https://geo-attendance-api.onrender.com/api/health`

You should see:
```json
{
  "status": "healthy",
  "message": "Geolocation Attendance System API is running"
}
```

---

## Step 8: Update Firebase Client (if using Option B)

If you used Option B for Firebase credentials, update `backend/firebase_client.py`:

```python
import os
import json
from firebase_admin import credentials, initialize_app, firestore, storage

def get_firebase_app():
    # Check if app is already initialized
    try:
        from firebase_admin import get_app
        return get_app()
    except ValueError:
        pass
    
    # Initialize with credentials from environment
    creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
    if creds_json:
        cred_dict = json.loads(creds_json)
        cred = credentials.Certificate(cred_dict)
    else:
        cred_path = os.getenv('FIREBASE_CREDENTIALS', 'firebase-credentials.json')
        cred = credentials.Certificate(cred_path)
    
    return initialize_app(cred, {
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
    })
```

Then push to GitHub:
```bash
git add .
git commit -m "Update Firebase config for Render"
git push
```

Render will auto-deploy the update!

---

## Step 9: Deploy Frontend on Vercel

Now let's deploy the frontend:

### 1. Update Frontend Environment

Create/edit `frontend/.env.production`:

```env
VITE_API_URL=https://geo-attendance-api.onrender.com/api
```

### 2. Install Vercel CLI

```bash
npm install -g vercel
```

### 3. Deploy

```bash
cd frontend
vercel login
vercel --prod
```

Follow prompts:
- **Set up and deploy**: Yes
- **Link to existing project**: No
- **Project name**: `geo-attendance`
- **Directory**: `./` (current)
- **Override settings**: No

Wait 1-2 minutes, then copy your live URL!

---

## Step 10: Update CORS (Important!)

1. Go back to **Render dashboard**
2. Click your service: `geo-attendance-api`
3. Go to **"Environment"** tab
4. Edit `CORS_ORIGINS` variable:
   - **Old value**: `*`
   - **New value**: `https://your-vercel-app.vercel.app`
5. Click **"Save Changes"**

Render will auto-redeploy with new CORS settings.

---

## 🎉 You're Live!

Your app is now deployed:
- **Backend**: https://geo-attendance-api.onrender.com
- **Frontend**: https://your-app.vercel.app

Test it:
1. Visit your frontend URL
2. Register a new account (Gmail only)
3. Login
4. Try all features!

---

## Important Notes

### ⚠️ Cold Starts
Free tier on Render **sleeps after 15 minutes** of inactivity.

First request after sleep takes **30 seconds** to wake up.

Solution: Use a free uptime monitor like:
- https://uptimerobot.com (pings every 5 minutes to keep awake)

### 📊 Free Tier Limits

**Render Free:**
- 750 hours/month (enough for 24/7)
- 512MB RAM
- Auto-sleep after 15 min

**Vercel Free:**
- 100GB bandwidth/month
- Unlimited deployments
- No sleep!

**Firebase Free:**
- 50K document reads/day
- 20K document writes/day
- 1GB storage

Perfect for your attendance system! 🚀

---

## Troubleshooting

### "Application failed to respond"
- Check Render logs for Python errors
- Ensure `gunicorn` is in `requirements.txt` ✅ (it is)
- Verify all environment variables are set

### "CORS error" in browser
- Update `CORS_ORIGINS` in Render with exact Vercel URL
- No trailing slash: ✅ `https://app.vercel.app` ❌ `https://app.vercel.app/`

### Firebase auth fails
- Check `FIREBASE_CREDENTIALS_JSON` is complete JSON
- Verify project ID matches Firebase console

### 500 errors
- View Render logs: Dashboard → Your Service → Logs
- Check for missing environment variables
- Ensure `firebase-credentials.json` is valid

---

## Next Steps

1. ✅ Set up custom domain (optional)
2. ✅ Add uptime monitor to prevent cold starts
3. ✅ Enable Firebase security rules
4. ✅ Set up automated backups
5. ✅ Monitor usage in Render/Vercel dashboards

**Deployment complete!** Your attendance system is live and free! 🎊
