"""Admin routes - Firestore backed"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, timezone

from middleware.auth import role_required, log_activity
from services.firestore_users import (
    list_users,
    get_user_by_id,
    update_user,
    deactivate_user,
    activate_user,
    lock_user,
    unlock_user,
    reset_password,
    delete_user,
    create_user,
)
from services.firestore_attendance import (
    list_attendance,
    update_attendance,
    delete_attendance,
    lock_attendance,
)
from services.firestore_devices import (
    list_devices,
    block_device,
    unblock_device,
    list_blocked_ips,
    block_ip,
    unblock_ip,
    get_all_settings,
    set_setting,
)
from services.firestore_classes import list_classes
from services.firestore_auth import get_user_by_email, log_audit
from utils.helpers import validate_email, validate_password, get_client_ip

admin_bp = Blueprint('admin', __name__)

# ==================== USER MANAGEMENT ====================

@admin_bp.route('/users', methods=['GET'])
@role_required('ADMIN')
def get_users():
    """Get all users with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role')
    search = request.args.get('search')
    is_active = request.args.get('is_active')
    if is_active:
        is_active = is_active.lower() == 'true'
    
    users, total = list_users(page, per_page, role, search, is_active)
    users = [{k: v for k, v in u.items() if k != 'password_hash'} for u in users]
    
    log_activity('list_users', 'user', None, {'filters': {'role': role, 'search': search}})
    
    return jsonify({'users': users, 'total': total, 'page': page, 'per_page': per_page}), 200


@admin_bp.route('/users', methods=['POST'])
@role_required('ADMIN')
def create_user_endpoint():
    """Create a new user"""
    data = request.get_json()
    required = ['email', 'full_name', 'role']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400

    is_valid, msg = validate_email(data['email'])
    if not is_valid:
        return jsonify({'error': msg}), 400

    if get_user_by_email(data['email']):
        return jsonify({'error': 'Email already exists'}), 400

    if data['role'] not in ['ADMIN', 'TEACHER', 'STUDENT']:
        return jsonify({'error': 'Invalid role'}), 400

    if 'password' in data:
        is_valid, msg = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': msg}), 400
    else:
        data['password'] = 'TempPassword@123'

    user = create_user(data)
    log_activity('user_created', 'user', user['id'], {'email': user['email'], 'role': user['role']})

    return jsonify({'message': 'User created', 'user': {k: v for k, v in user.items() if k != 'password_hash'}}), 201


@admin_bp.route('/users/<user_id>', methods=['PUT'])
@role_required('ADMIN')
def update_user_endpoint(user_id):
    """Update user info"""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    allowed = ['full_name', 'phone', 'student_id', 'employee_id']
    payload = {k: v for k, v in data.items() if k in allowed}

    updated = update_user(user_id, payload)
    log_activity('user_updated', 'user', user_id, payload)

    return jsonify({'message': 'User updated', 'user': {k: v for k, v in updated.items() if k != 'password_hash'}}), 200


@admin_bp.route('/users/<user_id>/deactivate', methods=['POST'])
@role_required('ADMIN')
def deactivate_user_endpoint(user_id):
    """Deactivate user"""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    deactivate_user(user_id)
    log_activity('user_deactivated', 'user', user_id)

    return jsonify({'message': 'User deactivated'}), 200


@admin_bp.route('/users/<user_id>/activate', methods=['POST'])
@role_required('ADMIN')
def activate_user_endpoint(user_id):
    """Activate user"""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    activate_user(user_id)
    log_activity('user_activated', 'user', user_id)

    return jsonify({'message': 'User activated'}), 200


@admin_bp.route('/users/<user_id>/lock', methods=['POST'])
@role_required('ADMIN')
def lock_user_endpoint(user_id):
    """Lock user account"""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    duration = data.get('duration', 24)

    lock_user(user_id, duration * 60)
    log_activity('user_locked', 'user', user_id, {'duration_hours': duration})

    return jsonify({'message': 'User locked'}), 200


@admin_bp.route('/users/<user_id>/unlock', methods=['POST'])
@role_required('ADMIN')
def unlock_user_endpoint(user_id):
    """Unlock user account"""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    unlock_user(user_id)
    log_activity('user_unlocked', 'user', user_id)

    return jsonify({'message': 'User unlocked'}), 200


@admin_bp.route('/users/<user_id>/reset-password', methods=['POST'])
@role_required('ADMIN')
def reset_password_endpoint(user_id):
    """Reset user password"""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    new_password = data.get('password', 'TempPassword@123')

    reset_password(user_id, new_password)
    log_activity('password_reset', 'user', user_id)

    return jsonify({'message': 'Password reset', 'temporary_password': new_password}), 200


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@role_required('ADMIN')
def delete_user_endpoint(user_id):
    """Delete a user"""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    delete_user(user_id)
    log_activity('user_deleted', 'user', user_id, {'email': user['email']})

    return jsonify({'message': 'User deleted'}), 200


# ==================== SYSTEM SETTINGS ====================

@admin_bp.route('/settings', methods=['GET'])
@role_required('ADMIN')
def get_settings():
    """Get all system settings"""
    settings = get_all_settings()
    log_activity('list_settings', 'settings')

    return jsonify({'settings': list(settings.values())}), 200


@admin_bp.route('/settings/<key>', methods=['PUT'])
@role_required('ADMIN')
def update_setting(key):
    """Update a system setting"""
    data = request.get_json()
    if 'value' not in data:
        return jsonify({'error': 'Value required'}), 400

    setting = set_setting(key, data['value'], data.get('data_type', 'string'), data.get('description'))
    log_activity('setting_updated', 'settings', key, {'value': data['value']})

    return jsonify({'message': 'Setting updated', 'setting': setting}), 200


# ==================== ATTENDANCE MANAGEMENT ====================

@admin_bp.route('/attendance', methods=['GET'])
@role_required('ADMIN')
def get_attendance():
    """Get all attendance records"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    class_id = request.args.get('class_id')
    student_id = request.args.get('student_id')
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    date_from_obj = None
    date_to_obj = None
    if date_from:
        date_from_obj = datetime.fromisoformat(date_from)
    if date_to:
        date_to_obj = datetime.fromisoformat(date_to)

    records, total = list_attendance(class_id, student_id, date_from_obj, date_to_obj, status, page, per_page)

    log_activity('list_attendance', 'attendance', None, {'filters': {
        'class_id': class_id, 'student_id': student_id, 'status': status
    }})

    return jsonify({'attendance': records, 'total': total, 'page': page, 'per_page': per_page}), 200


@admin_bp.route('/attendance/<record_id>', methods=['PUT'])
@role_required('ADMIN')
def update_attendance_record(record_id):
    """Update attendance record"""
    data = request.get_json()
    allowed = ['status', 'notes', 'distance', 'face_match_score']
    payload = {k: v for k, v in data.items() if k in allowed}

    updated = update_attendance(record_id, payload)
    log_activity('attendance_updated', 'attendance', record_id, payload)

    return jsonify({'message': 'Attendance updated', 'attendance': updated}), 200


@admin_bp.route('/attendance/<record_id>', methods=['DELETE'])
@role_required('ADMIN')
def delete_attendance_record(record_id):
    """Delete attendance record"""
    delete_attendance(record_id)
    log_activity('attendance_deleted', 'attendance', record_id)

    return jsonify({'message': 'Attendance deleted'}), 200


# ==================== DEVICE MANAGEMENT ====================

@admin_bp.route('/devices', methods=['GET'])
@role_required('ADMIN')
def get_all_devices():
    """Get all devices"""
    devices = list_devices()
    log_activity('list_devices', 'device')

    return jsonify({'devices': devices}), 200


@admin_bp.route('/devices/<device_id>/block', methods=['POST'])
@role_required('ADMIN')
def block_device_endpoint(device_id):
    """Block a device"""
    block_device(device_id)
    log_activity('device_blocked', 'device', device_id)

    return jsonify({'message': 'Device blocked'}), 200


# ==================== BLOCKED IPS ====================

@admin_bp.route('/blocked-ips', methods=['GET'])
@role_required('ADMIN')
def get_blocked_ips():
    """Get all blocked IPs"""
    ips = list_blocked_ips()
    log_activity('list_blocked_ips', 'blocked_ip')

    return jsonify({'blocked_ips': ips}), 200


@admin_bp.route('/blocked-ips', methods=['POST'])
@role_required('ADMIN')
def block_ip_endpoint():
    """Block an IP address"""
    data = request.get_json()
    if 'ip_address' not in data:
        return jsonify({'error': 'IP address required'}), 400

    user_id = get_jwt_identity()
    blocked = block_ip(
        data['ip_address'],
        reason=data.get('reason'),
        duration_hours=data.get('duration'),
        blocked_by=user_id,
    )
    log_activity('ip_blocked', 'blocked_ip', blocked['id'], {'ip': data['ip_address']})

    return jsonify({'message': 'IP blocked', 'blocked_ip': blocked}), 201


@admin_bp.route('/blocked-ips/<ip_id>', methods=['DELETE'])
@role_required('ADMIN')
def unblock_ip_endpoint(ip_id):
    """Unblock an IP address"""
    unblock_ip(ip_id)
    log_activity('ip_unblocked', 'blocked_ip', ip_id)

    return jsonify({'message': 'IP unblocked'}), 200


# ==================== STATISTICS ====================

@admin_bp.route('/statistics', methods=['GET'])
@role_required('ADMIN')
def get_statistics():
    """Get system statistics"""
    users, total_users = list_users()
    students = [u for u in users if u.get('role') == 'STUDENT']
    teachers = [u for u in users if u.get('role') == 'TEACHER']

    classes = list_classes()
    active_classes = [c for c in classes if c.get('is_active')]

    attendance, total_attendance = list_attendance()
    today = datetime.now(timezone.utc).date()
    today_attendance = [
        a for a in attendance
        if isinstance(a.get('timestamp'), datetime)
        and a.get('timestamp').date() == today
    ]

    log_activity('view_statistics', 'statistics')

    return jsonify({
        'statistics': {
            'total_users': len(users),
            'total_students': len(students),
            'total_teachers': len(teachers),
            'total_classes': len(classes),
            'active_classes': len(active_classes),
            'total_attendance': total_attendance,
            'today_attendance': len(today_attendance),
        }
    }), 200
