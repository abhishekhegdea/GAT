from datetime import datetime, timedelta, timezone
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from middleware.auth import ip_not_blocked, log_activity
from services.firestore_auth import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_login_failure,
    reset_login_attempts,
    update_last_login,
    upsert_device,
    verify_password,
    change_password as fs_change_password,
)
from utils.helpers import validate_email, validate_password, get_client_ip
from firebase_client import get_db
import os

auth_bp = Blueprint('auth', __name__)

# Temporary storage for verification codes (in production, use Redis)
verification_codes = {}

def send_verification_email(email, code, full_name):
    """Send verification email with code. Returns (sent_ok, dev_mode, error_msg)."""
    sender_email = os.getenv('MAIL_USERNAME')
    sender_password = os.getenv('MAIL_PASSWORD')
    mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = int(os.getenv('MAIL_PORT', 587))
    mail_use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'

    dev_mode = not (sender_email and sender_password)

    try:
        # Development mode: just log the code
        if dev_mode:
            print(f"DEV MODE: Verification code for {email}: {code}")
            return True, True, None

        message = MIMEMultipart('alternative')
        message['Subject'] = 'Email Verification - Attendance System'
        message['From'] = sender_email
        message['To'] = email

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #1F3C88;">Verify Your Email</h2>
                    <p>Hi {full_name},</p>
                    <p>Welcome to the Attendance System! Please use the verification code below to complete your registration:</p>
                    <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center;">
                        <h3 style="font-size: 32px; color: #00E5FF; letter-spacing: 5px; margin: 0;">{code}</h3>
                    </div>
                    <p style="color: #666;">This code will expire in 10 minutes.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="color: #999; font-size: 12px;">Attendance System - Geolocation & Face Recognition</p>
                </div>
            </body>
        </html>
        """

        part = MIMEText(html, 'html')
        message.attach(part)

        # Send via SMTP
        with smtplib.SMTP(mail_server, mail_port, timeout=15) as server:
            if mail_use_tls:
                server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [email], message.as_string())

        return True, False, None
    except Exception as e:
        error_msg = str(e)
        print(f"Error sending email: {error_msg}")
        return False, dev_mode, error_msg



@auth_bp.route('/register', methods=['POST'])
@ip_not_blocked
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'full_name', 'role', 'phone']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    email = data['email'].lower()
    
    # Validate Gmail only
    if not email.endswith('@gmail.com'):
        return jsonify({'error': 'Only Google (gmail.com) emails are allowed'}), 400
    
    # Validate email
    is_valid, message = validate_email(email)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Validate password
    is_valid, message = validate_password(data['password'])
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Check if user exists
    existing = get_user_by_email(email)
    if existing:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Validate role
    if data['role'] not in ['ADMIN', 'TEACHER', 'STUDENT']:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Create user
    created = create_user({
        'email': email,
        'password': data['password'],
        'full_name': data['full_name'],
        'role': data['role'],
        'phone': data['phone'],
        'email_verified': True,
        'student_id': data.get('student_id'),
        'employee_id': data.get('employee_id'),
    })
    
    log_activity('user_registered', 'user', created['id'], {'email': created['email'], 'role': created['role'], 'phone': created['phone']})
    
    return jsonify({
        'message': 'User registered successfully',
        'success': True,
        'user': {k: v for k, v in created.items() if k != 'password'}
    }), 201

@auth_bp.route('/login', methods=['POST'])
@ip_not_blocked
def login():
    """Login user"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email'].lower()
    if not email.endswith('@gmail.com'):
        return jsonify({'error': 'Only Google (gmail.com) emails are allowed'}), 400
    
    # Find user
    user = get_user_by_email(email)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check if account is locked
    locked_until = user.get('locked_until')
    if user.get('is_locked'):
        if locked_until and locked_until > datetime.now(timezone.utc):
            return jsonify({'error': 'Account is temporarily locked. Please try again later.'}), 403
        else:
            # Unlock account if lock period has expired
            reset_login_attempts(user['id'])

    # Check if account is active
    if not user.get('is_active', False):
        return jsonify({'error': 'Account is inactive. Please contact administrator.'}), 403
    
    # Verify password
    if not verify_password(user.get('password_hash'), data['password']):
        attempts = int(user.get('login_attempts', 0)) + 1
        _, is_locked, locked_until = update_login_failure(user['id'], attempts)
        if is_locked:
            log_activity('account_locked', 'user', user['id'], {'reason': 'Too many failed login attempts'})
            return jsonify({'error': 'Account locked due to too many failed login attempts'}), 403
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Reset login attempts on successful login
    reset_login_attempts(user['id'])
    update_last_login(user['id'])
    
    device_fingerprint = data.get('device_fingerprint', 'unknown')
    upsert_device(
        user_id=user['id'],
        device_fingerprint=device_fingerprint,
        device_payload={
            'device_name': data.get('device_name'),
            'browser': data.get('browser'),
            'os': data.get('os'),
            'ip_address': get_client_ip(request),
        }
    )
    
    # Create tokens
    access_token = create_access_token(identity=user['id'])
    refresh_token = create_refresh_token(identity=user['id'])
    
    log_activity('user_login', 'user', user['id'], {'device_fingerprint': device_fingerprint})
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {k: v for k, v in user.items() if k != 'password_hash'}
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    
    return jsonify({
        'access_token': access_token
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': {k: v for k, v in user.items() if k != 'password_hash'}
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    user_id = get_jwt_identity()
    log_activity('user_logout', 'user', user_id)
    
    # In a production system, you would add the token to a blacklist here
    
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new passwords are required'}), 400
    
    # Verify current password
    if not verify_password(user.get('password_hash'), data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Validate new password
    is_valid, message = validate_password(data['new_password'])
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Update password
    fs_change_password(user['id'], data['new_password'])
    
    log_activity('password_changed', 'user', user['id'])
    
    return jsonify({'message': 'Password changed successfully'}), 200
