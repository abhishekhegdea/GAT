# API Documentation

Base URL: `http://localhost:5000/api`

## Authentication

All protected endpoints require JWT authentication via `Authorization: Bearer <token>` header.

### Auth Endpoints

#### POST /auth/login
Login user and receive JWT tokens.

**Request:**
```json
{
  "email": "admin@system.com",
  "password": "Admin@123",
  "device_fingerprint": "device-id",
  "device_name": "Chrome/Windows",
  "browser": "Chrome",
  "os": "Windows"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "admin@system.com",
    "full_name": "System Administrator",
    "role": "ADMIN"
  }
}
```

#### POST /auth/refresh
Refresh access token using refresh token.

#### GET /auth/me
Get current user information.

#### POST /auth/logout
Logout user.

#### POST /auth/change-password
Change user password.

---

## Admin Endpoints

### User Management

#### GET /admin/users
Get all users with pagination and filtering.

**Query Parameters:**
- `page` (int): Page number
- `per_page` (int): Items per page
- `role` (string): Filter by role (ADMIN, TEACHER, STUDENT)
- `search` (string): Search by name, email, or ID
- `is_active` (boolean): Filter by active status

#### POST /admin/users
Create a new user.

**Request:**
```json
{
  "email": "student@example.com",
  "password": "Student@123",
  "full_name": "John Doe",
  "role": "STUDENT",
  "phone": "+1234567890",
  "student_id": "STU001"
}
```

#### PUT /admin/users/{user_id}
Update user information.

#### DELETE /admin/users/{user_id}
Delete a user.

#### POST /admin/users/{user_id}/deactivate
Deactivate user account.

#### POST /admin/users/{user_id}/activate
Activate user account.

#### POST /admin/users/{user_id}/lock
Lock user account.

**Request:**
```json
{
  "duration": 24  // hours
}
```

#### POST /admin/users/{user_id}/unlock
Unlock user account.

#### POST /admin/users/{user_id}/reset-password
Reset user password.

#### POST /admin/users/{user_id}/reset-face
Reset user face data.

### System Settings

#### GET /admin/settings
Get all system settings.

#### PUT /admin/settings/{key}
Update a system setting.

**Request:**
```json
{
  "value": "true"
}
```

### Attendance Management

#### GET /admin/attendance
Get all attendance records.

**Query Parameters:**
- `class_id` (string)
- `student_id` (string)
- `date_from` (ISO datetime)
- `date_to` (ISO datetime)
- `status` (string): PRESENT, LATE, ABSENT

#### PUT /admin/attendance/{attendance_id}
Modify attendance record.

#### DELETE /admin/attendance/{attendance_id}
Delete attendance record.

#### POST /admin/attendance/{attendance_id}/lock
Lock attendance record.

### Monitoring

#### GET /admin/logs
Get audit logs.

**Query Parameters:**
- `action` (string)
- `user_id` (string)
- `entity_type` (string)
- `date_from` (ISO datetime)
- `date_to` (ISO datetime)

#### GET /admin/devices
Get all registered devices.

#### POST /admin/devices/{device_id}/block
Block a device.

#### GET /admin/blocked-ips
Get blocked IP addresses.

#### POST /admin/blocked-ips
Block an IP address.

**Request:**
```json
{
  "ip_address": "192.168.1.100",
  "reason": "Suspicious activity",
  "duration": 24  // hours (optional)
}
```

#### POST /admin/blocked-ips/{ip_id}/unblock
Unblock an IP address.

### Statistics

#### GET /admin/statistics
Get system statistics.

**Response:**
```json
{
  "statistics": {
    "total_users": 150,
    "total_students": 120,
    "total_teachers": 25,
    "total_classes": 30,
    "total_attendance": 5000,
    "active_classes": 28,
    "today_attendance": 85,
    "recent_logins": 95
  }
}
```

### Export

#### GET /admin/export/attendance
Export attendance records to CSV.

**Query Parameters:**
- `class_id` (string)
- `date_from` (ISO datetime)
- `date_to` (ISO datetime)

**Response:** CSV file download

---

## Teacher Endpoints

### Class Management

#### GET /teacher/classes
Get teacher's classes.

#### POST /teacher/classes
Create a new class.

**Request:**
```json
{
  "name": "Mathematics 101",
  "description": "Basic mathematics course",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "radius": 100,
  "start_time": "09:00",
  "end_time": "10:30",
  "days_of_week": ["Monday", "Wednesday", "Friday"],
  "is_active": true,
  "attendance_enabled": true
}
```

#### PUT /teacher/classes/{class_id}
Update class information.

#### DELETE /teacher/classes/{class_id}
Delete a class.

#### GET /teacher/classes/{class_id}/students
Get students enrolled in class.

#### POST /teacher/classes/{class_id}/students
Enroll a student in class.

**Request:**
```json
{
  "student_id": "uuid"
}
```

#### DELETE /teacher/classes/{class_id}/students/{student_id}
Remove student from class.

### Attendance

#### GET /teacher/classes/{class_id}/attendance
Get attendance records for class.

**Query Parameters:**
- `date_from` (ISO datetime)
- `date_to` (ISO datetime)

#### PUT /teacher/attendance/{attendance_id}
Edit attendance record (if not locked).

#### GET /teacher/classes/{class_id}/export
Export class attendance to CSV.

---

## Student Endpoints

### Profile

#### GET /student/profile
Get student profile and enrolled classes.

**Response:**
```json
{
  "profile": {
    "id": "uuid",
    "email": "student@example.com",
    "full_name": "John Doe",
    "student_id": "STU001",
    "has_face_registered": true
  },
  "has_face_registered": true,
  "enrolled_classes": [
    {
      "id": "uuid",
      "name": "Mathematics 101",
      "start_time": "09:00",
      "end_time": "10:30",
      "is_active": true
    }
  ]
}
```

#### POST /student/register-face
Register face for attendance.

**Request:** multipart/form-data
- `image` (file): Face image

### Classes

#### GET /student/classes
Get enrolled classes.

### Attendance

#### GET /student/attendance/history
Get attendance history.

**Query Parameters:**
- `class_id` (string)
- `date_from` (ISO datetime)
- `date_to` (ISO datetime)
- `page` (int)
- `per_page` (int)

#### GET /student/attendance/statistics
Get attendance statistics.

**Query Parameters:**
- `class_id` (string)

**Response:**
```json
{
  "statistics": {
    "total": 50,
    "present": 45,
    "late": 3,
    "absent": 2,
    "attendance_rate": 90.0
  }
}
```

---

## Attendance Endpoints

### Mark Attendance

#### POST /attendance/mark
Mark attendance with geolocation and time verification.

**Request:** application/json
- `class_id` (string): Required
- `latitude` (float): Required
- `longitude` (float): Required
- `device_id` (string): Optional

**Response:**
```json
{
  "message": "Attendance marked successfully",
  "attendance": {
    "id": "uuid",
    "status": "PRESENT",
    "distance": 45.23,
    "timestamp": "2025-12-17T10:30:00Z"
  }
}
```

#### POST /attendance/validate-location
Validate if student is within attendance radius (without marking).

**Request:**
```json
{
  "class_id": "uuid",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

**Response:**
```json
{
  "is_valid": true,
  "distance": 45.23,
  "allowed_radius": 100,
  "message": "Within radius"
}
```

#### GET /attendance/check-eligibility/{class_id}
Check if student is eligible to mark attendance.

**Response:**
```json
{
  "eligible": true,
  "class": {
    "id": "uuid",
    "name": "Mathematics 101",
    "start_time": "09:00",
    "end_time": "10:30"
  },
  "message": "You can mark attendance now"
}
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "error": "Error message",
  "message": "Detailed error description",
  "timestamp": "2025-12-17T10:30:00Z"
}
```

Common HTTP status codes:
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Rate Limiting

API endpoints are rate-limited:
- Login: 5 attempts per 15 minutes per IP
- General endpoints: 100 requests per minute per user

---

## WebSocket (Future Enhancement)

Real-time attendance updates via WebSocket:
- Endpoint: `ws://localhost:5000/ws/attendance`
- Authentication: JWT token in query string
- Events: `attendance_marked`, `class_status_changed`
