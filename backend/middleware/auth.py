from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import json

from services.firestore_auth import (
    get_user_by_id,
    check_ip_blocked as fs_check_ip_blocked,
    log_audit,
)

def token_required(fn):
    """Decorator to require valid JWT token"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid or expired token', 'message': str(e)}), 401
    return wrapper

def role_required(*allowed_roles):
    """Decorator to require specific role(s)"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = get_user_by_id(user_id)

                if not user:
                    return jsonify({'error': 'User not found'}), 404
                
                if not user.get('is_active', False):
                    return jsonify({'error': 'Account is inactive'}), 403
                
                if user.get('is_locked', False):
                    return jsonify({'error': 'Account is locked'}), 403
                
                if user.get('role') not in allowed_roles:
                    return jsonify({'error': 'Insufficient permissions', 'required_role': allowed_roles}), 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Authorization failed', 'message': str(e)}), 401
        return wrapper
    return decorator

def get_current_user():
    """Get current authenticated user"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return get_user_by_id(user_id)
    except:
        return None

def check_ip_blocked():
    """Check if IP is blocked"""
    ip_address = request.remote_addr
    return fs_check_ip_blocked(ip_address)

def ip_not_blocked(fn):
    """Decorator to check if IP is not blocked"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if check_ip_blocked():
            return jsonify({'error': 'Your IP address has been blocked'}), 403
        return fn(*args, **kwargs)
    return wrapper

def admin_only(fn):
    """Shortcut decorator for admin-only routes"""
    return role_required('ADMIN')(token_required(fn))

def teacher_or_admin(fn):
    """Decorator for teacher or admin access"""
    return role_required('TEACHER', 'ADMIN')(token_required(fn))

def student_only(fn):
    """Decorator for student-only access"""
    return role_required('STUDENT')(token_required(fn))

def log_activity(action, entity_type=None, entity_id=None, details=None):
    """Log user activity to audit log"""
    try:
        user = get_current_user()
        user_id = user.get('id') if user else None
        log_audit(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            details=details,
            ip=request.remote_addr,
            ua=request.headers.get('User-Agent')
        )
    except Exception as e:
        print(f"Error logging activity: {e}")
