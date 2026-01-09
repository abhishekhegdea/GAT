# Geolocation-Based Attendance System with Face Recognition

A complete end-to-end attendance management system with geolocation validation, face recognition, and comprehensive role-based access control.

## Features

### Role-Based Access Control
- **Admin**: Full system control, user management, system configuration, monitoring
- **Teacher**: Class management, attendance oversight, location setup
- **Student**: Attendance marking with face + location verification

### Core Capabilities
- ✅ Geolocation validation using HTML5 API
- ✅ Face recognition (registration & verification)
- ✅ Mobile-first responsive design
- ✅ PWA support for offline capability
- ✅ Real-time attendance tracking
- ✅ Comprehensive audit logging
- ✅ Export reports (CSV/Excel/PDF)
- ✅ Device binding & IP tracking
- ✅ Fraud detection & prevention

## Tech Stack

**Frontend:**
- React.js 18
- Tailwind CSS
- TensorFlow.js (face recognition)
- Leaflet (map integration)
- PWA capabilities

**Backend:**
- Python Flask
- JWT Authentication
- PostgreSQL
- OpenCV & face_recognition
- RESTful APIs

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Firebase project with Firestore (Native mode) and Storage enabled

### Firebase Setup (frontend)
1. Create a Firebase project at https://console.firebase.google.com
2. Add a Web app, enable Hosting, and copy the config values (API key, auth domain, project ID, storage bucket, sender ID, app ID, measurement ID)
3. In `frontend/.env` set:
```
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
VITE_FIREBASE_MEASUREMENT_ID=your_measurement_id
```
4. To use Firebase services in the app, import `firebase.js` helpers:
```
import { auth, db, storage, analyticsPromise } from "./firebase";
```

### Automated Setup (Recommended)

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

### Manual Installation

1. **Clone and setup backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Firebase backend:**
```bash
# In backend/.env (or copy .env.example):
FIREBASE_CREDENTIALS=./firebase-service-account.json
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com

# Place your Firebase service account JSON at backend/firebase-service-account.json
```

3. **Initialize database:**
```bash
python init_db.py
```

4. **Run backend:**
```bash
python app.py
```

5. **Setup frontend:**
```bash
cd frontend
npm install
npm run dev
```

6. **Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000/api

### Default Admin Credentials
```
Email: admin@system.com
Password: Admin@123
```

## Project Structure

```
Geo-location/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration
│   ├── models/                # Database models
│   ├── routes/                # API endpoints
│   ├── services/              # Business logic
│   ├── middleware/            # Auth & authorization
│   ├── utils/                 # Utilities
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── utils/             # Utilities
│   │   └── App.js
│   └── package.json
└── README.md
```

## Documentation

- **[API Documentation](./API.md)** - Complete REST API reference with all endpoints
- **[Deployment Guide](./DEPLOYMENT.md)** - Production deployment (Docker, Nginx, SSL, monitoring)
- **Setup Scripts** - [setup.sh](./setup.sh) (Linux/macOS) | [setup.bat](./setup.bat) (Windows)

## Security Features

- JWT authentication with refresh tokens
- Role-based authorization
- Device fingerprinting
- IP logging and blocking
- Encrypted face data storage
- Audit trail for all operations
- HTTPS enforcement (production)

## Mobile Support

The application is fully responsive and works seamlessly on:
- iOS Safari
- Android Chrome
- Progressive Web App (PWA) installable

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please create an issue in the repository.
