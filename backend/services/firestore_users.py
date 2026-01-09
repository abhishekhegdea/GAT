"""Firestore users/admin management layer"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Tuple

from firebase_client import get_db
from services.firestore_auth import verify_password, _utcnow

USERS_COL = "users"


def list_users(
    page: int = 1,
    per_page: int = 20,
    role: str = None,
    search: str = None,
    is_active: bool = None,
) -> Tuple[List[dict], int]:
    """List users with filtering and pagination"""
    db = get_db()
    query = db.collection(USERS_COL)

    # Apply filters
    if role:
        query = query.where("role", "==", role)
    if is_active is not None:
        query = query.where("is_active", "==", is_active)

    # Count total before pagination
    docs = list(query.stream())
    total = len(docs)

    # Apply search filter (on email/name, done client-side)
    if search:
        search_lower = search.lower()
        docs = [
            d
            for d in docs
            if search_lower in d.to_dict().get("email", "").lower()
            or search_lower in d.to_dict().get("full_name", "").lower()
            or search_lower in d.to_dict().get("student_id", "").lower()
            or search_lower in d.to_dict().get("employee_id", "").lower()
        ]

    # Paginate
    start = (page - 1) * per_page
    paginated = docs[start : start + per_page]

    result = []
    for doc in paginated:
        data = doc.to_dict()
        data["id"] = doc.id
        result.append(data)

    return result, total


def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID"""
    db = get_db()
    doc = db.collection(USERS_COL).document(user_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    db = get_db()
    docs = db.collection(USERS_COL).where("email", "==", email.lower()).limit(1).stream()
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None


def create_user(payload: dict) -> dict:
    """Create a new user"""
    db = get_db()
    user_id = payload.get("id") or str(uuid.uuid4())
    now = _utcnow()

    from werkzeug.security import generate_password_hash

    db.collection(USERS_COL).document(user_id).set(
        {
            "email": payload["email"].lower(),
            "password_hash": generate_password_hash(payload.get("password", "")),
            "full_name": payload["full_name"],
            "role": payload["role"],
            "phone": payload.get("phone"),
            "student_id": payload.get("student_id"),
            "employee_id": payload.get("employee_id"),
            "is_active": True,
            "is_locked": False,
            "login_attempts": 0,
            "locked_until": None,
            "created_at": now,
            "updated_at": now,
            "last_login": None,
        }
    )
    return get_user_by_id(user_id)


def update_user(user_id: str, payload: dict) -> dict:
    """Update user fields"""
    db = get_db()
    update_data = {k: v for k, v in payload.items() if k not in ["id", "password_hash", "login_attempts"]}
    update_data["updated_at"] = _utcnow()
    db.collection(USERS_COL).document(user_id).update(update_data)
    return get_user_by_id(user_id)


def deactivate_user(user_id: str):
    """Deactivate user"""
    db = get_db()
    db.collection(USERS_COL).document(user_id).update(
        {"is_active": False, "updated_at": _utcnow()}
    )


def activate_user(user_id: str):
    """Activate user"""
    db = get_db()
    db.collection(USERS_COL).document(user_id).update(
        {"is_active": True, "updated_at": _utcnow()}
    )


def lock_user(user_id: str, duration_minutes: int = 30):
    """Lock user account"""
    db = get_db()
    locked_until = _utcnow() + __import__('datetime').timedelta(minutes=duration_minutes)
    db.collection(USERS_COL).document(user_id).update(
        {"is_locked": True, "locked_until": locked_until, "updated_at": _utcnow()}
    )


def unlock_user(user_id: str):
    """Unlock user account"""
    db = get_db()
    db.collection(USERS_COL).document(user_id).update(
        {
            "is_locked": False,
            "locked_until": None,
            "login_attempts": 0,
            "updated_at": _utcnow(),
        }
    )


def reset_password(user_id: str, password: str):
    """Reset user password"""
    from werkzeug.security import generate_password_hash

    db = get_db()
    db.collection(USERS_COL).document(user_id).update(
        {
            "password_hash": generate_password_hash(password),
            "updated_at": _utcnow(),
        }
    )


def delete_user(user_id: str):
    """Delete a user and related data"""
    db = get_db()
    # Delete user
    db.collection(USERS_COL).document(user_id).delete()
    # Delete devices
    device_docs = db.collection("devices").where("user_id", "==", user_id).stream()
    for doc in device_docs:
        doc.reference.delete()
    # Delete enrollments where student
    enroll_docs = (
        db.collection("enrollments").where("student_id", "==", user_id).stream()
    )
    for doc in enroll_docs:
        doc.reference.delete()
    # Delete classes where teacher
    class_docs = db.collection("classes").where("teacher_id", "==", user_id).stream()
    for doc in class_docs:
        doc.reference.delete()


def user_to_dict(user: dict) -> dict:
    """Convert user doc to response dict (hide sensitive fields)"""
    if not user:
        return None
    return {
        k: v
        for k, v in user.items()
        if k not in ["password_hash", "login_attempts"]
    }
