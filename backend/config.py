import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost/attendance_system')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # JWT Configuration
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 30)))
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS
    cors_env = os.getenv('CORS_ORIGINS', 'http://localhost:3000')
    CORS_ORIGINS = cors_env.split(',') if cors_env != '*' else '*'
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    FACE_IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'faces')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # System Settings
    DEFAULT_ATTENDANCE_RADIUS = int(os.getenv('DEFAULT_ATTENDANCE_RADIUS', 100))  # meters
    MAX_ATTENDANCE_RADIUS = int(os.getenv('MAX_ATTENDANCE_RADIUS', 500))  # meters
    FACE_RECOGNITION_ENABLED = os.getenv('FACE_RECOGNITION_ENABLED', 'True').lower() == 'true'
    GEOLOCATION_ENABLED = os.getenv('GEOLOCATION_ENABLED', 'True').lower() == 'true'
    FACE_MATCH_THRESHOLD = float(os.getenv('FACE_MATCH_THRESHOLD', 0.6))
    
    # Time Buffers
    EARLY_ENTRY_BUFFER = int(os.getenv('EARLY_ENTRY_BUFFER', 15))  # minutes
    LATE_ENTRY_BUFFER = int(os.getenv('LATE_ENTRY_BUFFER', 15))  # minutes
    
    # Security
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 30  # minutes
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/attendance_system_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
