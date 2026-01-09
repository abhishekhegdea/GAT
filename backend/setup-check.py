#!/usr/bin/env python3
"""
Initial setup script for Firebase deployment
Run this after downloading service account JSON
"""

import os
import sys
import json
from pathlib import Path


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_section(text):
    print(f"\n📌 {text}\n")


def check_firebase_credentials():
    """Check if Firebase credentials exist"""
    print_section("1. Checking Firebase Credentials")
    
    creds_path = Path("firebase-credentials.json")
    if creds_path.exists():
        try:
            with open(creds_path) as f:
                creds = json.load(f)
            project_id = creds.get("project_id")
            print(f"✅ Credentials found for project: {project_id}")
            return project_id
        except Exception as e:
            print(f"❌ Error reading credentials: {e}")
            return None
    else:
        print("❌ firebase-credentials.json not found")
        print("\n📥 To fix this:")
        print("  1. Go to https://console.firebase.google.com")
        print("  2. Select your project")
        print("  3. Click Settings (gear) → Service Accounts")
        print("  4. Click 'Generate New Private Key'")
        print("  5. Save as 'firebase-credentials.json' in backend folder")
        return None


def check_env_file():
    """Check if .env file exists and has required variables"""
    print_section("2. Checking Environment Configuration")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("\n📝 To fix this:")
        print("  1. Copy .env.example to .env")
        print("  2. Edit .env with your Firebase details")
        print("  3. Generate strong SECRET_KEY and JWT_SECRET_KEY")
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required = [
            "FIREBASE_PROJECT_ID",
            "FIREBASE_STORAGE_BUCKET",
            "FIREBASE_CREDENTIALS",
            "SECRET_KEY",
            "JWT_SECRET_KEY",
        ]
        
        missing = [var for var in required if not os.getenv(var)]
        
        if missing:
            print(f"❌ Missing environment variables: {', '.join(missing)}")
            print("\n📝 Update your .env file with these variables")
            return False
        
        print("✅ Environment variables configured")
        
        # Check for weak keys
        secret_key = os.getenv("SECRET_KEY")
        jwt_key = os.getenv("JWT_SECRET_KEY")
        
        if len(secret_key) < 32:
            print(f"⚠️  SECRET_KEY is weak ({len(secret_key)} chars, need 32+)")
        else:
            print(f"✅ SECRET_KEY is strong ({len(secret_key)} chars)")
        
        if len(jwt_key) < 32:
            print(f"⚠️  JWT_SECRET_KEY is weak ({len(jwt_key)} chars, need 32+)")
        else:
            print(f"✅ JWT_SECRET_KEY is strong ({len(jwt_key)} chars)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading .env: {e}")
        return False


def check_dependencies():
    """Check if required Python packages are installed"""
    print_section("3. Checking Python Dependencies")
    
    try:
        import firebase_admin
        print("✅ firebase-admin installed")
    except ImportError:
        print("❌ firebase-admin not installed")
        print("\n   Install with: pip install firebase-admin")
        return False
    
    try:
        import flask
        print("✅ Flask installed")
    except ImportError:
        print("❌ Flask not installed")
        print("\n   Install with: pip install -r requirements-prod.txt")
        return False
    
    try:
        from flask_jwt_extended import JWTManager
        print("✅ Flask-JWT-Extended installed")
    except ImportError:
        print("❌ Flask-JWT-Extended not installed")
        return False
    
    return True


def test_firebase_connection():
    """Test Firebase connection"""
    print_section("4. Testing Firebase Connection")
    
    try:
        from firebase_client import get_db
        db = get_db()
        
        # Try to access system_settings
        docs = db.collection("system_settings").limit(1).stream()
        print("✅ Firebase connection successful")
        
        # Check if collections exist
        collections = [
            "users", "classes", "enrollments", "attendance",
            "devices", "audit_logs", "blocked_ips", "system_settings"
        ]
        
        print(f"\n📚 Checking Firestore collections:")
        for collection in collections:
            try:
                db.collection(collection).limit(1).stream()
                print(f"   ✅ {collection}")
            except Exception as e:
                print(f"   ❌ {collection}: {str(e)[:50]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        print("\n   Check:")
        print("   1. FIREBASE_PROJECT_ID is correct")
        print("   2. firebase-credentials.json exists and is valid")
        print("   3. Firestore Database is enabled")
        print("   4. You have internet connection")
        return False


def check_gitignore():
    """Check if sensitive files are in .gitignore"""
    print_section("5. Checking Git Security")
    
    gitignore_path = Path(".gitignore")
    
    if not gitignore_path.exists():
        print("⚠️  .gitignore not found")
        return False
    
    with open(gitignore_path) as f:
        gitignore_content = f.read()
    
    sensitive_files = [
        ".env",
        "firebase-credentials.json",
        "*.key",
        "secrets/",
    ]
    
    all_ignored = True
    for file in sensitive_files:
        if file in gitignore_content:
            print(f"✅ {file} is in .gitignore")
        else:
            print(f"❌ {file} is NOT in .gitignore")
            all_ignored = False
    
    if not all_ignored:
        print("\n⚠️  Add these to .gitignore to avoid committing secrets!")
    
    return all_ignored


def main():
    print_header("Firebase Deployment Setup Check")
    
    checks = [
        ("Firebase Credentials", check_firebase_credentials()),
        ("Environment Configuration", check_env_file()),
        ("Python Dependencies", check_dependencies()),
    ]
    
    # Only test connection if basic checks pass
    if checks[0][1] and checks[1][1]:
        checks.append(("Firebase Connection", test_firebase_connection()))
    
    check_gitignore()
    
    print_header("Setup Check Summary")
    
    all_passed = all(result for _, result in checks if result is not None and result is not False)
    
    for name, result in checks:
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{status:12} {name}")
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to:")
        print("  1. Run: python bootstrap_firestore.py")
        print("  2. Start server: python app.py")
        print("  3. Test: curl http://localhost:5000/api/health")
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        print("\n📚 For help, see:")
        print("  - DEPLOYMENT_READY.md - Quick start guide")
        print("  - FIREBASE_DEPLOYMENT_SETUP.md - Complete setup guide")
        print("  - PRE_DEPLOYMENT_CHECKLIST.md - Pre-deployment checklist")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
