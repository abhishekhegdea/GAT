from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # ADMIN, TEACHER, STUDENT
    is_active = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20))
    student_id = db.Column(db.String(50), unique=True, nullable=True)  # For students
    employee_id = db.Column(db.String(50), unique=True, nullable=True)  # For teachers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Relationships
    face_encodings = db.relationship('FaceEncoding', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='student', lazy='dynamic', foreign_keys='Attendance.student_id')
    created_classes = db.relationship('Class', backref='teacher', lazy='dynamic', foreign_keys='Class.teacher_id')
    devices = db.relationship('Device', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic', foreign_keys='AuditLog.user_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'phone': self.phone,
            'student_id': self.student_id,
            'employee_id': self.employee_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }
        if include_sensitive:
            data['login_attempts'] = self.login_attempts
            data['locked_until'] = self.locked_until.isoformat() if self.locked_until else None
        return data

class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius = db.Column(db.Integer, default=100)  # meters
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    days_of_week = db.Column(db.String(50))  # JSON string: ["Monday", "Wednesday"]
    is_active = db.Column(db.Boolean, default=True)
    attendance_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('ClassEnrollment', backref='class_obj', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='class_obj', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.full_name if self.teacher else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius': self.radius,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'days_of_week': self.days_of_week,
            'is_active': self.is_active,
            'attendance_enabled': self.attendance_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class ClassEnrollment(db.Model):
    __tablename__ = 'class_enrollments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = db.Column(db.String(36), db.ForeignKey('classes.id'), nullable=False)
    student_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    student = db.relationship('User', backref='enrollments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'class_id': self.class_id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'is_active': self.is_active,
        }

class FaceEncoding(db.Model):
    __tablename__ = 'face_encodings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    encoding = db.Column(db.LargeBinary, nullable=False)  # Stored as binary
    image_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
        }

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.String(36), db.ForeignKey('classes.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float)  # Distance from class location in meters
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    face_match_score = db.Column(db.Float)
    device_id = db.Column(db.String(36), db.ForeignKey('devices.id'))
    status = db.Column(db.String(20), default='PRESENT')  # PRESENT, LATE, ABSENT
    ip_address = db.Column(db.String(45))
    is_locked = db.Column(db.Boolean, default=False)
    is_valid = db.Column(db.Boolean, default=True)
    marked_by = db.Column(db.String(36), db.ForeignKey('users.id'))  # For manual marking
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    marker = db.relationship('User', foreign_keys=[marked_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'class_id': self.class_id,
            'class_name': self.class_obj.name if self.class_obj else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'distance': self.distance,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'face_match_score': self.face_match_score,
            'status': self.status,
            'ip_address': self.ip_address,
            'is_locked': self.is_locked,
            'is_valid': self.is_valid,
            'notes': self.notes,
        }

class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    device_fingerprint = db.Column(db.String(255), nullable=False)
    device_name = db.Column(db.String(255))
    browser = db.Column(db.String(100))
    os = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    is_blocked = db.Column(db.Boolean, default=False)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_fingerprint': self.device_fingerprint,
            'device_name': self.device_name,
            'browser': self.browser,
            'os': self.os,
            'ip_address': self.ip_address,
            'is_blocked': self.is_blocked,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False, index=True)
    entity_type = db.Column(db.String(50))  # user, class, attendance, etc.
    entity_id = db.Column(db.String(36))
    details = db.Column(db.Text)  # JSON string with details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else 'System',
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    data_type = db.Column(db.String(20), default='string')  # string, int, float, bool, json
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'data_type': self.data_type,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class BlockedIP(db.Model):
    __tablename__ = 'blocked_ips'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ip_address = db.Column(db.String(45), unique=True, nullable=False, index=True)
    reason = db.Column(db.Text)
    blocked_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    blocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'reason': self.reason,
            'blocked_at': self.blocked_at.isoformat() if self.blocked_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
        }
