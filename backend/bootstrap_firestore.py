"""Bootstrap Firestore database with default data"""
import os
from dotenv import load_dotenv

# Load .env BEFORE importing firebase_client
load_dotenv()

from datetime import datetime, timedelta
from firebase_client import get_db, get_bucket
from services.firestore_auth import create_user, _utcnow

def bootstrap_firestore():
    """Initialize Firestore with default collections and data"""
    db = get_db()
    
    print("🔥 Bootstrapping Firestore...")
    
    # 1. Create default admin user
    print("\n📝 Creating default admin user...")
    try:
        admin_user = create_user({
            'email': 'admin@system.com',
            'password': 'Admin@123',
            'first_name': 'System',
            'last_name': 'Admin',
            'role': 'ADMIN',
            'is_active': True,
            'is_locked': False,
        })
        print(f"✅ Admin user created: {admin_user['id']}")
    except Exception as e:
        print(f"⚠️  Admin user already exists or error: {e}")
    
    # 2. Initialize system settings
    print("\n⚙️  Initializing system settings...")
    settings = {
        'attendance_radius': 100,  # meters
        'max_login_attempts': 5,
        'account_lock_duration': 900,  # 15 minutes
        'ip_block_duration': 3600,  # 1 hour
        'auto_attendance_timeout': 300,  # 5 minutes
        'late_marking_minutes': 15,  # mark as late if after start_time + 15 mins
    }
    
    settings_ref = db.collection('system_settings')
    for key, value in settings.items():
        try:
            settings_ref.document(key).set({
                'key': key,
                'value': value,
                'type': type(value).__name__,
                'updated_at': _utcnow(),
            })
            print(f"✅ Setting '{key}' = {value}")
        except Exception as e:
            print(f"⚠️  Setting '{key}' error: {e}")
    
    # 3. Ensure collections exist with indexes
    print("\n📚 Initializing collections...")
    collections_to_init = [
        'users',
        'classes',
        'enrollments',
        'attendance',
        'devices',
        'audit_logs',
        'blocked_ips',
    ]
    
    for collection_name in collections_to_init:
        try:
            # Just verify collection exists by checking if we can read from it
            docs = db.collection(collection_name).limit(1).stream()
            print(f"✅ Collection '{collection_name}' ready")
        except Exception as e:
            print(f"⚠️  Collection '{collection_name}' error: {e}")
    
    # 4. Create sample test data (optional)
    print("\n🧪 Creating sample test users...")
    test_users = [
        {
            'email': 'teacher@test.com',
            'password': 'Teacher@123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'TEACHER',
            'is_active': True,
        },
        {
            'email': 'student@test.com',
            'password': 'Student@123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'STUDENT',
            'is_active': True,
        },
    ]
    
    for user_data in test_users:
        try:
            user = create_user(user_data)
            print(f"✅ Test user created: {user_data['email']}")
        except Exception as e:
            print(f"⚠️  Test user '{user_data['email']}' error: {e}")
    
    print("\n🎉 Firestore bootstrap completed!")
    print("\nDefault credentials:")
    print("  Admin: admin@system.com / Admin@123")
    print("  Teacher: teacher@test.com / Teacher@123")
    print("  Student: student@test.com / Student@123")

if __name__ == '__main__':
    bootstrap_firestore()
