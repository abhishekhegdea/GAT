import face_recognition
import cv2
import numpy as np
from PIL import Image
import io
import pickle
import base64

def encode_face(image_data):
    """
    Encode face from image data
    Returns face encoding or None if no face found
    """
    try:
        # Convert image data to numpy array
        if isinstance(image_data, bytes):
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            image = cv2.imread(image_data)
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find face locations
        face_locations = face_recognition.face_locations(rgb_image)
        
        if len(face_locations) == 0:
            return None, "No face detected in image"
        
        if len(face_locations) > 1:
            return None, "Multiple faces detected. Please ensure only one face is visible"
        
        # Get face encoding
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        if len(face_encodings) == 0:
            return None, "Could not generate face encoding"
        
        return face_encodings[0], None
    
    except Exception as e:
        return None, f"Error encoding face: {str(e)}"

def verify_face(known_encoding, image_data, tolerance=0.6):
    """
    Verify face against known encoding
    Returns (match, confidence_score)
    """
    try:
        # Get encoding from new image
        new_encoding, error = encode_face(image_data)
        
        if error:
            return False, 0.0, error
        
        # Compare faces
        results = face_recognition.compare_faces([known_encoding], new_encoding, tolerance=tolerance)
        
        # Calculate distance (lower is better match)
        distance = face_recognition.face_distance([known_encoding], new_encoding)[0]
        
        # Convert distance to confidence score (0-1, higher is better)
        confidence = 1 - distance
        
        return results[0], round(confidence, 4), None
    
    except Exception as e:
        return False, 0.0, f"Error verifying face: {str(e)}"

def serialize_encoding(encoding):
    """Convert face encoding to bytes for database storage"""
    return pickle.dumps(encoding)

def deserialize_encoding(encoding_bytes):
    """Convert bytes back to face encoding"""
    return pickle.loads(encoding_bytes)

def detect_liveness(image_data):
    """
    Basic liveness detection
    Returns (is_live, message)
    
    Note: This is a basic implementation. For production,
    consider using more advanced liveness detection methods.
    """
    try:
        # Convert image data to numpy array
        if isinstance(image_data, bytes):
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            image = cv2.imread(image_data)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance (blur detection)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # If variance is too low, image might be a photo of a photo
        if laplacian_var < 100:
            return False, "Image quality too low or potential spoof detected"
        
        # Check brightness
        mean_brightness = np.mean(gray)
        if mean_brightness < 40 or mean_brightness > 220:
            return False, "Poor lighting conditions"
        
        return True, "Liveness check passed"
    
    except Exception as e:
        return False, f"Error in liveness detection: {str(e)}"

def validate_face_image(image_data, max_size_mb=5):
    """
    Validate face image quality and requirements
    """
    try:
        # Check file size
        if isinstance(image_data, bytes):
            size_mb = len(image_data) / (1024 * 1024)
            if size_mb > max_size_mb:
                return False, f"Image size exceeds {max_size_mb}MB limit"
            
            # Convert to image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            image = cv2.imread(image_data)
        
        if image is None:
            return False, "Invalid image format"
        
        # Check dimensions
        height, width = image.shape[:2]
        if width < 200 or height < 200:
            return False, "Image resolution too low (minimum 200x200)"
        
        if width > 4000 or height > 4000:
            return False, "Image resolution too high (maximum 4000x4000)"
        
        # Check if face is detectable
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        
        if len(face_locations) == 0:
            return False, "No face detected in image"
        
        if len(face_locations) > 1:
            return False, "Multiple faces detected. Please ensure only one face is visible"
        
        return True, "Image validation passed"
    
    except Exception as e:
        return False, f"Error validating image: {str(e)}"
