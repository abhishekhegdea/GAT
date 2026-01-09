"""Firestore attendance management layer"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from firebase_client import get_db
from services.firestore_auth import _utcnow

ATTENDANCE_COL = "attendance"


def create_attendance(payload: dict) -> dict:
    """Create an attendance record"""
    db = get_db()
    record_id = str(uuid.uuid4())
    now = _utcnow()

    db.collection(ATTENDANCE_COL).document(record_id).set(
        {
            "student_id": payload["student_id"],
            "class_id": payload["class_id"],
            "latitude": float(payload["latitude"]),
            "longitude": float(payload["longitude"]),
            "distance": payload.get("distance"),
            "timestamp": now,
            "face_match_score": payload.get("face_match_score"),
            "device_id": payload.get("device_id"),
            "status": payload.get("status", "PRESENT"),  # PRESENT, LATE, ABSENT
            "ip_address": payload.get("ip_address"),
            "is_locked": False,
            "is_valid": payload.get("is_valid", True),
            "marked_by": payload.get("marked_by"),
            "notes": payload.get("notes"),
            "created_at": now,
            "updated_at": now,
        }
    )
    return get_attendance_by_id(record_id)


def get_attendance_by_id(record_id: str) -> Optional[dict]:
    """Get attendance record by ID"""
    db = get_db()
    doc = db.collection(ATTENDANCE_COL).document(record_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def list_attendance(
    class_id: str = None,
    student_id: str = None,
    date_from: datetime = None,
    date_to: datetime = None,
    status: str = None,
    page: int = 1,
    per_page: int = 20,
) -> Tuple[List[dict], int]:
    """List attendance records with filtering"""
    db = get_db()
    query = db.collection(ATTENDANCE_COL)

    if class_id:
        query = query.where("class_id", "==", class_id)
    if student_id:
        query = query.where("student_id", "==", student_id)
    if status:
        query = query.where("status", "==", status)
    if date_from:
        query = query.where("timestamp", ">=", date_from)
    if date_to:
        query = query.where("timestamp", "<=", date_to)

    docs = list(query.stream())
    total = len(docs)

    # Paginate
    start = (page - 1) * per_page
    paginated = docs[start : start + per_page]

    result = []
    for doc in paginated:
        data = doc.to_dict()
        data["id"] = doc.id
        result.append(data)

    return result, total


def update_attendance(record_id: str, payload: dict) -> dict:
    """Update attendance record"""
    db = get_db()
    update_data = {k: v for k, v in payload.items() if k not in ["id", "created_at", "student_id", "class_id"]}
    update_data["updated_at"] = _utcnow()
    db.collection(ATTENDANCE_COL).document(record_id).update(update_data)
    return get_attendance_by_id(record_id)


def lock_attendance(record_id: str):
    """Lock attendance record"""
    db = get_db()
    db.collection(ATTENDANCE_COL).document(record_id).update(
        {"is_locked": True, "updated_at": _utcnow()}
    )


def delete_attendance(record_id: str):
    """Delete attendance record"""
    db = get_db()
    db.collection(ATTENDANCE_COL).document(record_id).delete()


def check_duplicate_attendance(student_id: str, class_id: str, date_str: str = None) -> bool:
    """Check if student marked attendance for class today"""
    db = get_db()
    query = (
        db.collection(ATTENDANCE_COL)
        .where("student_id", "==", student_id)
        .where("class_id", "==", class_id)
    )

    # If date provided, filter by that date
    if date_str:
        from datetime import datetime as dt

        date_start = dt.fromisoformat(date_str)
        date_end = date_start.replace(hour=23, minute=59, second=59)
        query = query.where("timestamp", ">=", date_start).where("timestamp", "<=", date_end)

    for _ in query.limit(1).stream():
        return True
    return False


def get_attendance_stats(student_id: str = None, class_id: str = None) -> dict:
    """Get attendance statistics"""
    db = get_db()
    query = db.collection(ATTENDANCE_COL)

    if student_id:
        query = query.where("student_id", "==", student_id)
    if class_id:
        query = query.where("class_id", "==", class_id)

    total = 0
    present = 0
    late = 0
    absent = 0

    for doc in query.stream():
        data = doc.to_dict()
        total += 1
        status = data.get("status", "ABSENT")
        if status == "PRESENT":
            present += 1
        elif status == "LATE":
            late += 1
        else:
            absent += 1

    rate = (present / total * 100) if total > 0 else 0

    return {
        "total": total,
        "present": present,
        "late": late,
        "absent": absent,
        "attendance_rate": round(rate, 2),
    }
