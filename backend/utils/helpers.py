import hashlib
import secrets
from datetime import datetime, timedelta

def generate_device_id(user_agent, ip_address):
    """Generate unique device fingerprint"""
    data = f"{user_agent}{ip_address}{secrets.token_hex(16)}"
    return hashlib.sha256(data.encode()).hexdigest()

def validate_password(password):
    """
    Validate password strength
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, "Email is valid"
    return False, "Invalid email format"

def paginate_query(query, page=1, per_page=20):
    """
    Paginate SQLAlchemy query
    Returns (items, total_pages, total_items)
    """
    total_items = query.count()
    total_pages = (total_items + per_page - 1) // per_page
    
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return items, total_pages, total_items

def format_response(data=None, message=None, error=None, status_code=200):
    """Standardized API response format"""
    response = {}
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if error:
        response['error'] = error
    
    response['timestamp'] = datetime.utcnow().isoformat()
    
    return response, status_code

def allowed_file(filename, allowed_extensions={'png', 'jpg', 'jpeg'}):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_client_ip(request):
    """Get client IP address from request"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr
