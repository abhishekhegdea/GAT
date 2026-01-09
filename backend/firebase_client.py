"""Firebase initialization (Firestore + Storage)"""
import json
import os
from functools import lru_cache

import firebase_admin
from firebase_admin import credentials, firestore, storage


def _load_credentials():
    """Load Firebase credentials from environment or file"""
    # Option 1: Load from JSON string in environment variable (for Render/Railway)
    creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if creds_json:
        try:
            cred_dict = json.loads(creds_json)
            return credentials.Certificate(cred_dict)
        except json.JSONDecodeError as e:
            print(f"Error parsing FIREBASE_CREDENTIALS_JSON: {e}")
    
    # Option 2: Load from file path
    creds_path = os.getenv("FIREBASE_CREDENTIALS", "firebase-credentials.json")
    if os.path.exists(creds_path):
        return credentials.Certificate(creds_path)
    
    # Option 3: Fallback to application default credentials
    print("Warning: Using Application Default Credentials")
    return credentials.ApplicationDefault()


@lru_cache(maxsize=1)
def get_firebase_app():
    if not firebase_admin._apps:
        cred = _load_credentials()
        options = {}
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        bucket = os.getenv("FIREBASE_STORAGE_BUCKET")
        if project_id:
            options["projectId"] = project_id
        if bucket:
            options["storageBucket"] = bucket
        firebase_admin.initialize_app(cred, options or None)
    return firebase_admin.get_app()


@lru_cache(maxsize=1)
def get_db():
    return firestore.client(app=get_firebase_app())


@lru_cache(maxsize=1)
def get_bucket():
    app = get_firebase_app()
    bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")
    if bucket_name:
        return storage.bucket(bucket_name, app=app)
    return storage.bucket(app=app)
