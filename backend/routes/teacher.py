"""Teacher routes - Firestore backed"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from middleware.auth import role_required, log_activity
from services.firestore_classes import (
    create_class, get_class_by_id, list_classes, update_class, delete_class,
    enroll_student, list_enrollments_for_class, remove_enrollment, get_enrollment_by_id
)
from services.firestore_users import get_user_by_id, get_user_by_email
from services.firestore_attendance import list_attendance, update_attendance
from services.firestore_auth import _utcnow

teacher_bp = Blueprint('teacher', __name__)

# ==================== CLASS MANAGEMENT ====================

@teacher_bp.route('/classes', methods=['GET'])
@role_required('TEACHER')
def get_teacher_classes():
    """Get all classes for teacher"""
    user_id = get_jwt_identity()
    
    classes = list_classes(teacher_id=user_id)
    
    log_activity('view_classes', 'class', None)
    
    return jsonify({'classes': classes}), 200


@teacher_bp.route('/classes', methods=['POST'])
@role_required('TEACHER')
def create_class_endpoint():
    """Create new class"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required = ['name', 'latitude', 'longitude', 'radius', 'start_time', 'end_time']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate numeric fields
    try:
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        radius = int(data['radius'])
    except ValueError:
        return jsonify({'error': 'Invalid coordinate or radius values'}), 400
    
    cls = create_class({
        'name': data['name'],
        'teacher_id': user_id,
        'latitude': latitude,
        'longitude': longitude,
        'radius': radius,
        'start_time': data['start_time'],
        'end_time': data['end_time'],
        'schedule': data.get('schedule', 'DAILY'),
        'description': data.get('description', ''),
        'is_active': True,
        'created_at': _utcnow(),
    })
    
    log_activity('class_created', 'class', cls['id'])
    
    return jsonify({'message': 'Class created successfully', 'class': cls}), 201


@teacher_bp.route('/classes/<class_id>', methods=['GET'])
@role_required('TEACHER')
def get_class_detail(class_id):
    """Get class details"""
    user_id = get_jwt_identity()
    
    cls = get_class_by_id(class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check ownership
    if cls['teacher_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    log_activity('view_class', 'class', class_id)
    
    return jsonify({'class': cls}), 200


@teacher_bp.route('/classes/<class_id>', methods=['PUT'])
@role_required('TEACHER')
def update_class_endpoint(class_id):
    """Update class"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    cls = get_class_by_id(class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check ownership
    if cls['teacher_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update fields
    update_data = {}
    for key in ['name', 'latitude', 'longitude', 'radius', 'start_time', 'end_time', 'schedule', 'description', 'is_active']:
        if key in data:
            update_data[key] = data[key]
    
    updated = update_class(class_id, update_data)
    
    log_activity('class_updated', 'class', class_id)
    
    return jsonify({'message': 'Class updated successfully', 'class': updated}), 200


@teacher_bp.route('/classes/<class_id>', methods=['DELETE'])
@role_required('TEACHER')
def delete_class_endpoint(class_id):
    """Delete class"""
    user_id = get_jwt_identity()
    
    cls = get_class_by_id(class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check ownership
    if cls['teacher_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    delete_class(class_id)
    
    log_activity('class_deleted', 'class', class_id)
    
    return jsonify({'message': 'Class deleted successfully'}), 200


# ==================== ENROLLMENT MANAGEMENT ====================

@teacher_bp.route('/classes/<class_id>/students', methods=['GET'])
@role_required('TEACHER')
def get_class_students(class_id):
    """Get all students in class"""
    user_id = get_jwt_identity()
    
    cls = get_class_by_id(class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check ownership
    if cls['teacher_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    enrollments = list_enrollments_for_class(class_id)
    
    # Enrich with student details
    students = []
    for enroll in enrollments:
        student = get_user_by_id(enroll['student_id'])
        if student:
            student['enrollment_id'] = enroll['id']
            student['enrolled_date'] = enroll.get('enrolled_date')
            students.append(student)
    
    log_activity('view_class_students', 'class', class_id)
    
    return jsonify({'students': students}), 200


@teacher_bp.route('/classes/<class_id>/students', methods=['POST'])
@role_required('TEACHER')
def enroll_student_endpoint(class_id):
    """Enroll student in class"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    cls = get_class_by_id(class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check ownership
    if cls['teacher_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    student_id = data.get('student_id')
    student_email = data.get('student_email')
    
    # Resolve student_id from email if needed
    if not student_id and student_email:
        student = get_user_by_email(student_email)
        if student:
            student_id = student['id']
    
    if not student_id:
        return jsonify({'error': 'Student not found'}), 404
    
    # Verify student exists and is a student
    student = get_user_by_id(student_id)
    if not student or student.get('role') != 'STUDENT':
        return jsonify({'error': 'Invalid student'}), 400
    
    enrollment = enroll_student(class_id, student_id)
    
    log_activity('student_enrolled', 'enrollment', enrollment['id'], {'class_id': class_id, 'student_id': student_id})
    
    return jsonify({'message': 'Student enrolled successfully', 'enrollment': enrollment}), 201


@teacher_bp.route('/classes/<class_id>/students/<student_id>', methods=['DELETE'])
@role_required('TEACHER')
def remove_student_endpoint(class_id, student_id):
    """Remove student from class"""
    user_id = get_jwt_identity()
    
    cls = get_class_by_id(class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check ownership
    if cls['teacher_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get enrollment to get its ID
    enrollments = list_enrollments_for_class(class_id)
    enrollment_id = None
    for enroll in enrollments:
        if enroll['student_id'] == student_id:
            enrollment_id = enroll['id']
            break
    
    if not enrollment_id:
        return jsonify({'error': 'Student not enrolled'}), 404
    
    remove_enrollment(enrollment_id)
    
    log_activity('student_removed', 'enrollment', enrollment_id, {'class_id': class_id, 'student_id': student_id})
    
    return jsonify({'message': 'Student removed from class'}), 200


# ==================== ATTENDANCE ====================

@teacher_bp.route('/classes/<class_id>/attendance', methods=['GET'])
@role_required('TEACHER')
def get_class_attendance(class_id):
    """Get attendance records for class"""
    user_id = get_jwt_identity()
    
    cls = get_class_by_id(class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check ownership
    if cls['teacher_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    student_id = request.args.get('student_id')
    status = request.args.get('status')
    
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
        student_id=student_id,
        date_from=date_from_obj,
        date_to=date_to_obj,
        status=status,
        page=page,
        per_page=per_page
    )
    
    # Enrich with student details
    for record in records:
        student = get_user_by_id(record['student_id'])
        if student:
            record['student_name'] = f"{student.get('first_name', '')} {student.get('last_name', '')}"
            record['student_email'] = student.get('email', '')
    
    log_activity('view_attendance', 'attendance', class_id)
    
    return jsonify({'attendance': records, 'total': total, 'page': page, 'per_page': per_page}), 200


@teacher_bp.route('/attendance/<attendance_id>', methods=['PUT'])
@role_required('TEACHER')
def edit_attendance(attendance_id):
    """Edit attendance record"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Note: Full attendance record lookup needed - for now assume teacher owns the class
    # In production, verify teacher owns the class that this attendance belongs to
    
    update_data = {}
    if 'status' in data:
        update_data['status'] = data['status']
    if 'is_valid' in data:
        update_data['is_valid'] = data['is_valid']
    
    updated = update_attendance(attendance_id, update_data)
    
    log_activity('attendance_updated', 'attendance', attendance_id)
    
    return jsonify({'message': 'Attendance updated', 'attendance': updated}), 200
