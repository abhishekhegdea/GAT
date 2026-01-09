from app import create_app
from models import db, User, SystemSetting
from datetime import datetime
import os

def init_database():
    """Initialize database with tables and default data"""
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")
        
        # Check if admin exists
        admin = User.query.filter_by(role='ADMIN').first()
        
        if not admin:
            print("\nCreating default admin user...")
            admin = User(
                email=os.getenv('ADMIN_EMAIL', 'admin@system.com'),
                full_name='System Administrator',
                role='ADMIN',
                is_active=True
            )
            admin.set_password(os.getenv('ADMIN_PASSWORD', 'Admin@123'))
            
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Admin user created: {admin.email}")
            print(f"  Password: {os.getenv('ADMIN_PASSWORD', 'Admin@123')}")
        else:
            print(f"\n✓ Admin user already exists: {admin.email}")
        
        # Create default system settings
        print("\nCreating default system settings...")
        
        default_settings = [
            {
                'key': 'face_recognition_enabled',
                'value': 'true',
                'data_type': 'bool',
                'description': 'Enable or disable face recognition globally'
            },
            {
                'key': 'geolocation_enabled',
                'value': 'true',
                'data_type': 'bool',
                'description': 'Enable or disable geolocation validation globally'
            },
            {
                'key': 'default_attendance_radius',
                'value': '100',
                'data_type': 'int',
                'description': 'Default attendance radius in meters'
            },
            {
                'key': 'max_attendance_radius',
                'value': '500',
                'data_type': 'int',
                'description': 'Maximum allowed attendance radius in meters'
            },
            {
                'key': 'face_match_threshold',
                'value': '0.6',
                'data_type': 'float',
                'description': 'Face matching confidence threshold (0-1)'
            },
            {
                'key': 'early_entry_buffer',
                'value': '15',
                'data_type': 'int',
                'description': 'Minutes before class start time to allow attendance'
            },
            {
                'key': 'late_entry_buffer',
                'value': '15',
                'data_type': 'int',
                'description': 'Minutes after class end time to allow attendance'
            }
        ]
        
        for setting_data in default_settings:
            existing = SystemSetting.query.filter_by(key=setting_data['key']).first()
            if not existing:
                setting = SystemSetting(**setting_data)
                db.session.add(setting)
                print(f"  ✓ Created setting: {setting_data['key']}")
            else:
                print(f"  - Setting already exists: {setting_data['key']}")
        
        db.session.commit()
        print("\n✓ Database initialization complete!")
        print("\n" + "="*50)
        print("Default Admin Credentials:")
        print(f"Email: {os.getenv('ADMIN_EMAIL', 'admin@system.com')}")
        print(f"Password: {os.getenv('ADMIN_PASSWORD', 'Admin@123')}")
        print("="*50)

if __name__ == '__main__':
    init_database()
