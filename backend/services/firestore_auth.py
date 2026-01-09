"""Firestore-based user/auth/device/audit helpers"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from werkzeug.security import generate_password_hash, check_password_hash

from firebase_client import get_db

USERS_COL = "users"
DEVICES_COL = "devices"
AUDIT_COL = "audit_logs"
BLOCKED_IPS_COL = "blocked_ips"


def _utcnow():
    return datetime.now(timezone.utc)


def user_to_dict(doc) -> dict:
    data = doc.to_dict() if hasattr(doc, "to_dict") else doc
    if not data:
        return None
    # Ensure id is included
    data.setdefault("id", doc.id if hasattr(doc, "id") else data.get("id"))
    # Normalize datetime fields to isoformat strings for API responses
    for key in ("created_at", "updated_at", "last_login", "locked_until"):
        if isinstance(data.get(key), datetime):
            data[key] = data[key].isoformat()
    return data


def get_user_by_email(email: str) -> Optional[dict]:
    db = get_db()
    docs = db.collection(USERS_COL).where("email", "==", email.lower()).limit(1).stream()
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None


def get_user_by_id(user_id: str) -> Optional[dict]:
    db = get_db()
    doc = db.collection(USERS_COL).document(user_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def create_user(payload: dict) -> dict:
    db = get_db()
    user_id = payload.get("id") or str(uuid.uuid4())
    now = _utcnow()
    doc_ref = db.collection(USERS_COL).document(user_id)
    doc_ref.set(
        {
            "email": payload["email"].lower(),
            "password_hash": generate_password_hash(payload["password"]),
            "full_name": payload["full_name"],
            "role": payload["role"],
            "phone": payload.get("phone"),
            "email_verified": payload.get("email_verified", False),
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
    return {"id": user_id, **payload, "is_active": True, "is_locked": False}


def verify_password(stored_hash: str, password: str) -> bool:
    return check_password_hash(stored_hash, password)


def update_login_failure(user_id: str, attempts: int, lock_minutes: int = 30) -> Tuple[int, bool, Optional[datetime]]:
    db = get_db()
    locked_until = None
    is_locked = False
    if attempts >= 5:
        is_locked = True
        locked_until = _utcnow() + timedelta(minutes=lock_minutes)
    db.collection(USERS_COL).document(user_id).update(
        {
            "login_attempts": attempts,
            "is_locked": is_locked,
            "locked_until": locked_until,
            "updated_at": _utcnow(),
        }
    )
    return attempts, is_locked, locked_until


def reset_login_attempts(user_id: str):
    db = get_db()
    db.collection(USERS_COL).document(user_id).update(
        {"login_attempts": 0, "is_locked": False, "locked_until": None, "updated_at": _utcnow()}
    )


def update_last_login(user_id: str):
    db = get_db()
    db.collection(USERS_COL).document(user_id).update(
        {"last_login": _utcnow(), "updated_at": _utcnow()}
    )


def upsert_device(user_id: str, device_fingerprint: str, device_payload: dict):
    db = get_db()
    device_id = f"{user_id}_{device_fingerprint}"
    now = _utcnow()
    db.collection(DEVICES_COL).document(device_id).set(
        {
            "id": device_id,
            "user_id": user_id,
            "device_fingerprint": device_fingerprint,
            "device_name": device_payload.get("device_name"),
            "browser": device_payload.get("browser"),
            "os": device_payload.get("os"),
            "ip_address": device_payload.get("ip_address"),
            "is_blocked": False,
            "first_seen": device_payload.get("first_seen") or now,
            "last_seen": now,
        },
        merge=True,
    )
    return device_id


def log_audit(action: str, entity_type: str = None, entity_id: str = None, user_id: str = None, details: dict = None, ip=None, ua=None):
    db = get_db()
    db.collection(AUDIT_COL).add(
        {
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "user_id": user_id,
            "details": details,
            "ip_address": ip,
            "user_agent": ua,
            "timestamp": _utcnow(),
        }
    )


def check_ip_blocked(ip_address: str) -> bool:
    if not ip_address:
        return False
    db = get_db()
    docs = (
        db.collection(BLOCKED_IPS_COL)
        .where("ip_address", "==", ip_address)
        .where("is_active", "==", True)
        .limit(1)
        .stream()
    )
    return any(True for _ in docs)


def change_password(user_id: str, new_password: str):
    db = get_db()
    db.collection(USERS_COL).document(user_id).update(
        {
            "password_hash": generate_password_hash(new_password),
            "updated_at": _utcnow(),
        }
    )
