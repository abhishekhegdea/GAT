import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
          headers: { Authorization: `Bearer ${refreshToken}` }
        });

        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  sendVerificationEmail: (data) => api.post('/auth/send-verification-email', data),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  changePassword: (data) => api.post('/auth/change-password', data),
};

// Admin API
export const adminAPI = {
  // Users
  getUsers: (params) => api.get('/admin/users', { params }),
  createUser: (userData) => api.post('/admin/users', userData),
  updateUser: (userId, userData) => api.put(`/admin/users/${userId}`, userData),
  deleteUser: (userId) => api.delete(`/admin/users/${userId}`),
  deactivateUser: (userId) => api.post(`/admin/users/${userId}/deactivate`),
  activateUser: (userId) => api.post(`/admin/users/${userId}/activate`),
  lockUser: (userId, data) => api.post(`/admin/users/${userId}/lock`, data),
  unlockUser: (userId) => api.post(`/admin/users/${userId}/unlock`),
  resetPassword: (userId, data) => api.post(`/admin/users/${userId}/reset-password`, data),
  resetFace: (userId) => api.post(`/admin/users/${userId}/reset-face`),
  
  // System Settings
  getSettings: () => api.get('/admin/settings'),
  updateSetting: (key, data) => api.put(`/admin/settings/${key}`, data),
  
  // Attendance
  getAllAttendance: (params) => api.get('/admin/attendance', { params }),
  updateAttendance: (attendanceId, data) => api.put(`/admin/attendance/${attendanceId}`, data),
  deleteAttendance: (attendanceId) => api.delete(`/admin/attendance/${attendanceId}`),
  lockAttendance: (attendanceId) => api.post(`/admin/attendance/${attendanceId}/lock`),
  
  // Classes
  getAllClasses: (params) => api.get('/admin/classes', { params }),
  
  // Monitoring
  getLogs: (params) => api.get('/admin/logs', { params }),
  getDevices: (params) => api.get('/admin/devices', { params }),
  blockDevice: (deviceId) => api.post(`/admin/devices/${deviceId}/block`),
  getBlockedIPs: () => api.get('/admin/blocked-ips'),
  blockIP: (data) => api.post('/admin/blocked-ips', data),
  unblockIP: (ipId) => api.post(`/admin/blocked-ips/${ipId}/unblock`),
  
  // Statistics
  getStatistics: () => api.get('/admin/statistics'),
  
  // Export
  exportAttendance: (params) => api.get('/admin/export/attendance', { params, responseType: 'blob' }),
};

// Teacher API
export const teacherAPI = {
  getMyClasses: () => api.get('/teacher/classes'),
  createClass: (classData) => api.post('/teacher/classes', classData),
  updateClass: (classId, classData) => api.put(`/teacher/classes/${classId}`, classData),
  deleteClass: (classId) => api.delete(`/teacher/classes/${classId}`),
  getClassStudents: (classId) => api.get(`/teacher/classes/${classId}/students`),
  enrollStudent: (classId, data) => api.post(`/teacher/classes/${classId}/students`, data),
  removeStudent: (classId, studentId) => api.delete(`/teacher/classes/${classId}/students/${studentId}`),
  getClassAttendance: (classId, params) => api.get(`/teacher/classes/${classId}/attendance`, { params }),
  editAttendance: (attendanceId, data) => api.put(`/teacher/attendance/${attendanceId}`, data),
  exportClassAttendance: (classId, params) => api.get(`/teacher/classes/${classId}/export`, { params, responseType: 'blob' }),
};

// Student API
export const studentAPI = {
  getProfile: () => api.get('/student/profile'),
  registerFace: (formData) => api.post('/student/register-face', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getEnrolledClasses: () => api.get('/student/classes'),
  getAttendanceHistory: (params) => api.get('/student/attendance/history', { params }),
  getAttendanceStatistics: (params) => api.get('/student/attendance/statistics', { params }),
};

// Attendance API
export const attendanceAPI = {
  markAttendance: (formData) => api.post('/attendance/mark', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  validateLocation: (data) => api.post('/attendance/validate-location', data),
  checkEligibility: (classId) => api.get(`/attendance/check-eligibility/${classId}`),
};

// Classes API
export const classesAPI = {
  getClasses: (params) => api.get('/classes', { params }),
  getClass: (classId) => api.get(`/classes/${classId}`),
};
