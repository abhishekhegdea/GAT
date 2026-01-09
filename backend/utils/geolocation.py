import math
from datetime import datetime, time, timedelta

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in meters
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    
    return c * r

def validate_location(student_lat, student_lon, class_lat, class_lon, allowed_radius):
    """
    Validate if student is within allowed radius of class location
    Returns (is_valid, distance)
    """
    distance = haversine_distance(student_lat, student_lon, class_lat, class_lon)
    is_valid = distance <= allowed_radius
    
    return is_valid, round(distance, 2)

def is_within_time_window(class_start_time, class_end_time, buffer_minutes=15):
    """
    Check if current time is within class time window (with buffer)
    """
    from datetime import datetime, time, timedelta
    
    current_time = datetime.now().time()
    
    # Add buffer to start time (allow early entry)
    start_with_buffer = (datetime.combine(datetime.today(), class_start_time) - 
                         timedelta(minutes=buffer_minutes)).time()
    
    # Add buffer to end time (allow late entry)
    end_with_buffer = (datetime.combine(datetime.today(), class_end_time) + 
                       timedelta(minutes=buffer_minutes)).time()
    
    return start_with_buffer <= current_time <= end_with_buffer
