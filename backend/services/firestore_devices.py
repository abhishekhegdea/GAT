"""Firestore device/settings management layer"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict

from firebase_client import get_db
from services.firestore_auth import _utcnow

DEVICES_COL = "devices"
SETTINGS_COL = "system_settings"
BLOCKED_IPS_COL = "blocked_ips"


# ============ Device Management ============
def list_devices(user_id: str = None) -> List[dict]:
    """List all devices or for a specific user"""
    db = get_db()
    query = db.collection(DEVICES_COL)
    if user_id:
        query = query.where("user_id", "==", user_id)

    result = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        result.append(data)
    return result


def get_device_by_id(device_id: str) -> Optional[dict]:
    """Get device by ID"""
    db = get_db()
    doc = db.collection(DEVICES_COL).document(device_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def block_device(device_id: str):
    """Block a device"""
    db = get_db()
    db.collection(DEVICES_COL).document(device_id).update(
        {"is_blocked": True, "updated_at": _utcnow()}
    )


def unblock_device(device_id: str):
    """Unblock a device"""
    db = get_db()
    db.collection(DEVICES_COL).document(device_id).update(
        {"is_blocked": False, "updated_at": _utcnow()}
    )


# ============ System Settings ============
def get_setting(key: str) -> Optional[dict]:
    """Get a system setting"""
    db = get_db()
    doc = db.collection(SETTINGS_COL).document(key).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def get_all_settings() -> Dict[str, dict]:
    """Get all system settings"""
    db = get_db()
    result = {}
    for doc in db.collection(SETTINGS_COL).stream():
        data = doc.to_dict()
        data["id"] = doc.id
        result[doc.id] = data
    return result


def set_setting(key: str, value: str, data_type: str = "string", description: str = None) -> dict:
    """Set a system setting"""
    db = get_db()
    now = _utcnow()
    db.collection(SETTINGS_COL).document(key).set(
        {
            "key": key,
            "value": str(value),
            "data_type": data_type,
            "description": description,
            "updated_at": now,
        },
        merge=True,
    )
    return get_setting(key)


# ============ Blocked IP Management ============
def list_blocked_ips() -> List[dict]:
    """List all blocked IPs"""
    db = get_db()
    result = []
    for doc in db.collection(BLOCKED_IPS_COL).where("is_active", "==", True).stream():
        data = doc.to_dict()
        data["id"] = doc.id
        result.append(data)
    return result


def block_ip(ip_address: str, reason: str = None, duration_hours: int = None, blocked_by: str = None) -> dict:
    """Block an IP address"""
    db = get_db()
    now = _utcnow()
    expires_at = None
    if duration_hours:
        expires_at = now + timedelta(hours=duration_hours)

    ip_id = str(uuid.uuid4())
    db.collection(BLOCKED_IPS_COL).document(ip_id).set(
        {
            "ip_address": ip_address,
            "reason": reason,
            "blocked_by": blocked_by,
            "blocked_at": now,
            "expires_at": expires_at,
            "is_active": True,
        }
    )
    return get_blocked_ip_by_id(ip_id)


def get_blocked_ip_by_id(ip_id: str) -> Optional[dict]:
    """Get blocked IP by ID"""
    db = get_db()
    doc = db.collection(BLOCKED_IPS_COL).document(ip_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def unblock_ip(ip_id: str):
    """Unblock an IP address"""
    db = get_db()
    db.collection(BLOCKED_IPS_COL).document(ip_id).update(
        {"is_active": False, "updated_at": _utcnow()}
    )


def check_ip_expired(ip_address: str) -> bool:
    """Check if blocked IP has expired"""
    db = get_db()
    now = _utcnow()
    docs = (
        db.collection(BLOCKED_IPS_COL)
        .where("ip_address", "==", ip_address)
        .where("is_active", "==", True)
        .stream()
    )
    for doc in docs:
        data = doc.to_dict()
        expires_at = data.get("expires_at")
        if expires_at and expires_at < now:
            # Expire the block
            db.collection(BLOCKED_IPS_COL).document(doc.id).update(
                {"is_active": False}
            )
            return True
    return False
