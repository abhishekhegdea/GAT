"""Firestore classes/enrollment management layer"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict

from firebase_client import get_db
from services.firestore_auth import _utcnow

CLASSES_COL = "classes"
ENROLLMENTS_COL = "enrollments"


def create_class(teacher_id: str, payload: dict) -> dict:
    """Create a new class"""
    db = get_db()
    class_id = str(uuid.uuid4())
    now = _utcnow()

    db.collection(CLASSES_COL).document(class_id).set(
        {
            "name": payload["name"],
            "description": payload.get("description"),
            "teacher_id": teacher_id,
            "latitude": float(payload["latitude"]),
            "longitude": float(payload["longitude"]),
            "radius": int(payload.get("radius", 100)),
            "start_time": payload.get("start_time"),  # HH:MM format
            "end_time": payload.get("end_time"),  # HH:MM format
            "days_of_week": payload.get("days_of_week", "[]"),  # JSON string
            "is_active": payload.get("is_active", True),
            "attendance_enabled": payload.get("attendance_enabled", True),
            "created_at": now,
            "updated_at": now,
        }
    )
    return get_class_by_id(class_id)


def get_class_by_id(class_id: str) -> Optional[dict]:
    """Get class by ID"""
    db = get_db()
    doc = db.collection(CLASSES_COL).document(class_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def list_classes(teacher_id: str = None, is_active: bool = None) -> List[dict]:
    """List classes with optional filtering"""
    db = get_db()
    query = db.collection(CLASSES_COL)

    if teacher_id:
        query = query.where("teacher_id", "==", teacher_id)
    if is_active is not None:
        query = query.where("is_active", "==", is_active)

    result = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        result.append(data)
    return result


def update_class(class_id: str, payload: dict) -> dict:
    """Update class"""
    db = get_db()
    update_data = {k: v for k, v in payload.items() if k not in ["id", "teacher_id", "created_at"]}
    update_data["updated_at"] = _utcnow()
    db.collection(CLASSES_COL).document(class_id).update(update_data)
    return get_class_by_id(class_id)


def delete_class(class_id: str):
    """Delete class and related enrollments"""
    db = get_db()
    # Delete enrollments
    enroll_docs = (
        db.collection(ENROLLMENTS_COL).where("class_id", "==", class_id).stream()
    )
    for doc in enroll_docs:
        doc.reference.delete()
    # Delete class
    db.collection(CLASSES_COL).document(class_id).delete()


def enroll_student(class_id: str, student_id: str) -> dict:
    """Enroll a student in a class"""
    db = get_db()
    enroll_id = f"{class_id}_{student_id}"
    now = _utcnow()

    db.collection(ENROLLMENTS_COL).document(enroll_id).set(
        {
            "class_id": class_id,
            "student_id": student_id,
            "enrolled_at": now,
            "is_active": True,
        }
    )
    return get_enrollment_by_id(enroll_id)


def get_enrollment_by_id(enroll_id: str) -> Optional[dict]:
    """Get enrollment by ID"""
    db = get_db()
    doc = db.collection(ENROLLMENTS_COL).document(enroll_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def list_enrollments_for_class(class_id: str) -> List[dict]:
    """List all enrollments for a class"""
    db = get_db()
    result = []
    for doc in db.collection(ENROLLMENTS_COL).where("class_id", "==", class_id).stream():
        data = doc.to_dict()
        data["id"] = doc.id
        result.append(data)
    return result


def list_enrollments_for_student(student_id: str) -> List[dict]:
    """List all classes a student is enrolled in"""
    db = get_db()
    result = []
    for doc in db.collection(ENROLLMENTS_COL).where("student_id", "==", student_id).stream():
        data = doc.to_dict()
        data["id"] = doc.id
        result.append(data)
    return result


def remove_enrollment(class_id: str, student_id: str):
    """Remove student from class"""
    db = get_db()
    enroll_id = f"{class_id}_{student_id}"
    db.collection(ENROLLMENTS_COL).document(enroll_id).delete()


def is_student_enrolled(class_id: str, student_id: str) -> bool:
    """Check if student is enrolled in class"""
    db = get_db()
    enroll_id = f"{class_id}_{student_id}"
    doc = db.collection(ENROLLMENTS_COL).document(enroll_id).get()
    return doc.exists
