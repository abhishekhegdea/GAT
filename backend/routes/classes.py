"""Public classes routes - Firestore backed"""
from flask import Blueprint, jsonify

from services.firestore_classes import list_classes

classes_bp = Blueprint('classes', __name__)

# ==================== PUBLIC CLASS LISTING ====================

@classes_bp.route('', methods=['GET'])
def get_all_classes():
    """Get all active classes"""
    classes = list_classes(is_active=True)
    
    return jsonify({'classes': classes}), 200
