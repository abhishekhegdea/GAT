"""Student routes - Firestore backed"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from middleware.auth import role_required, log_activity
from services.firestore_users import get_user_by_id
from services.firestore_classes import list_enrollments_for_student, get_class_by_id
from services.firestore_attendance import list_attendance, get_attendance_stats

student_bp = Blueprint('student', __name__)

# ==================== PROFILE ====================

@student_bp.route('/profile', methods=['GET'])
@role_required('STUDENT')
def get_profile():
    """Get student profile"""
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get enrolled classes
    enrollments = list_enrollments_for_student(user_id)
    enrolled_classes = []
    for enroll in enrollments:
        cls = get_class_by_id(enroll['class_id'])
        if cls:
            enrolled_classes.append(cls)
    
    profile_data = {k: v for k, v in user.items() if k != 'password_hash'}
    profile_data['enrolled_classes'] = enrolled_classes
    
    log_activity('view_profile', 'user', user_id)
    
    return jsonify({'profile': profile_data}), 200


# ==================== CLASSES ====================

@student_bp.route('/classes', methods=['GET'])
@role_required('STUDENT')
def get_enrolled_classes():
    """Get enrolled classes"""
    user_id = get_jwt_identity()
    
    enrollments = list_enrollments_for_student(user_id)
    classes = []
    for enroll in enrollments:
        cls = get_class_by_id(enroll['class_id'])
        if cls:
            classes.append(cls)
    
    log_activity('view_classes', 'class', None)
    
    return jsonify({'classes': classes}), 200


# ==================== ATTENDANCE ====================

@student_bp.route('/attendance/history', methods=['GET'])
@role_required('STUDENT')
def get_attendance_history():
    """Get attendance history"""
    user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    class_id = request.args.get('class_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    date_from_obj = None
    date_to_obj = None
    if date_from:
        from datetime import datetime
        date_from_obj = datetime.fromisoformat(date_from)
    if date_to:
        from datetime import datetime
        date_to_obj = datetime.fromisoformat(date_to)
    
    records, total = list_attendance(
        class_id=class_id,
        student_id=user_id,
        date_from=date_from_obj,
        date_to=date_to_obj,
        page=page,
        per_page=per_page
    )
    
    log_activity('view_attendance', 'attendance', None, {'class_id': class_id})
    
    return jsonify({'attendance': records, 'total': total, 'page': page, 'per_page': per_page}), 200


@student_bp.route('/attendance/statistics', methods=['GET'])
@role_required('STUDENT')
def get_attendance_statistics():
    """Get attendance statistics"""
    user_id = get_jwt_identity()
    
    class_id = request.args.get('class_id')
    
    stats = get_attendance_stats(student_id=user_id, class_id=class_id)
    
    log_activity('view_statistics', 'attendance', user_id)
    
    return jsonify({'statistics': stats}), 200
