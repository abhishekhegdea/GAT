"""Attendance marking routes - Firestore backed"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from middleware.auth import role_required, log_activity
from services.firestore_attendance import create_attendance, check_duplicate_attendance
from services.firestore_classes import get_class_by_id, is_student_enrolled
from utils.helpers import get_client_ip
from utils.geolocation import validate_location, is_within_time_window

attendance_bp = Blueprint('attendance', __name__)

# ==================== MARK ATTENDANCE ====================

@attendance_bp.route('/mark', methods=['POST'])
@role_required('STUDENT')
def mark_attendance():
    """Mark attendance with location verification"""
    user_id = get_jwt_identity()
    
    # Get required fields
    class_id = request.form.get('class_id')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    
    if not all([class_id, latitude, longitude]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify class exists
    cls = get_class_by_id(class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check enrollment
    if not is_student_enrolled(class_id, user_id):
        return jsonify({'error': 'Not enrolled in this class'}), 403
    
    # Check for duplicate
    if check_duplicate_attendance(user_id, class_id):
        return jsonify({'error': 'Already marked attendance for this class today'}), 400
    
    # Validate location
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({'error': 'Invalid coordinates'}), 400
    
    is_valid_loc, distance = validate_location(
        latitude, longitude,
        cls['latitude'], cls['longitude'],
        cls['radius']
    )
    
    if not is_valid_loc:
        return jsonify({'error': f'Too far from class location (distance: {distance}m, radius: {cls["radius"]}m)'}), 400
    
    # Check time window
    is_valid_time = is_within_time_window(cls['start_time'], cls['end_time'], early_buffer=15, late_buffer=15)
    if not is_valid_time:
        return jsonify({'error': 'Not within attendance time window'}), 400
    
    # Determine status
    from datetime import datetime
    now = datetime.now()
    start_time = cls.get('start_time')
    
    status = 'PRESENT'
    if start_time:
        try:
            start = datetime.strptime(start_time, '%H:%M').time()
            if now.time() > start:
                status = 'LATE'
        except:
            pass
    
    # Create attendance record
    attendance = create_attendance({
        'student_id': user_id,
        'class_id': class_id,
        'latitude': latitude,
        'longitude': longitude,
        'distance': distance,
        'status': status,
        'ip_address': get_client_ip(request),
        'is_valid': True,
    })
    
    log_activity('attendance_marked', 'attendance', attendance['id'], {
        'class_id': class_id,
        'status': status,
        'distance': distance
    })
    
    return jsonify({
        'message': f'Attendance marked as {status}',
        'attendance': attendance
    }), 201


# ==================== VALIDATION ====================

@attendance_bp.route('/validate-location', methods=['POST'])
@role_required('STUDENT')
def validate_location_endpoint():
    """Validate if student is within attendance radius"""
    data = request.get_json()
    
    class_id = data.get('class_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not all([class_id, latitude, longitude]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    cls = get_class_by_id(class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({'error': 'Invalid coordinates'}), 400
    
    is_valid, distance = validate_location(
        latitude, longitude,
        cls['latitude'], cls['longitude'],
        cls['radius']
    )
    
    return jsonify({
        'is_valid': is_valid,
        'distance': distance,
        'allowed_radius': cls['radius'],
        'message': 'Within radius' if is_valid else 'Too far from class location'
    }), 200


@attendance_bp.route('/check-eligibility/<class_id>', methods=['GET'])
@role_required('STUDENT')
def check_eligibility(class_id):
    """Check if student is eligible to mark attendance"""
    user_id = get_jwt_identity()
    
    # Check class exists
    cls = get_class_by_id(class_id)
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    
    # Check enrollment
    if not is_student_enrolled(class_id, user_id):
        return jsonify({'eligible': False, 'reason': 'Not enrolled in this class'}), 200
    
    # Check for duplicate today
    if check_duplicate_attendance(user_id, class_id):
        return jsonify({'eligible': False, 'reason': 'Already marked attendance today'}), 200
    
    # Check time window
    is_valid_time = is_within_time_window(cls['start_time'], cls['end_time'], early_buffer=15, late_buffer=15)
    if not is_valid_time:
        return jsonify({'eligible': False, 'reason': 'Not within attendance time window'}), 200
    
    log_activity('check_eligibility', 'attendance', class_id)
    
    return jsonify({
        'eligible': True,
        'class': cls,
        'message': 'You can mark attendance now'
    }), 200
