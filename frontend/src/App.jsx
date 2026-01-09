import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './components/ui/Toast';
import { ProtectedRoute, PublicRoute } from './components/ProtectedRoute';

// Auth Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import Unauthorized from './pages/auth/Unauthorized';

// Admin Pages
import AdminDashboard from './pages/admin/Dashboard';
import AdminUsers from './pages/admin/Users';
import AdminSettings from './pages/admin/Settings';
import AdminAttendance from './pages/admin/Attendance';
import AdminLogs from './pages/admin/Logs';

// Teacher Pages
import TeacherDashboard from './pages/teacher/Dashboard';
import TeacherClasses from './pages/teacher/Classes';
import TeacherAttendance from './pages/teacher/Attendance';

// Student Pages
import StudentDashboard from './pages/student/Dashboard';
import StudentAttendance from './pages/student/Attendance';
import StudentProfile from './pages/student/Profile';
import StudentFaceRegister from './pages/student/FaceRegister';

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          } />
          <Route path="/register" element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          } />
          <Route path="/unauthorized" element={<Unauthorized />} />

          {/* Admin Routes */}
          <Route path="/admin" element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path="/admin/users" element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <AdminUsers />
            </ProtectedRoute>
          } />
          <Route path="/admin/settings" element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <AdminSettings />
            </ProtectedRoute>
          } />
          <Route path="/admin/attendance" element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <AdminAttendance />
            </ProtectedRoute>
          } />
          <Route path="/admin/logs" element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <AdminLogs />
            </ProtectedRoute>
          } />

          {/* Teacher Routes */}
          <Route path="/teacher" element={
            <ProtectedRoute allowedRoles={['TEACHER', 'ADMIN']}>
              <TeacherDashboard />
            </ProtectedRoute>
          } />
          <Route path="/teacher/classes" element={
            <ProtectedRoute allowedRoles={['TEACHER', 'ADMIN']}>
              <TeacherClasses />
            </ProtectedRoute>
          } />
          <Route path="/teacher/attendance" element={
            <ProtectedRoute allowedRoles={['TEACHER', 'ADMIN']}>
              <TeacherAttendance />
            </ProtectedRoute>
          } />

          {/* Student Routes */}
          <Route path="/student" element={
            <ProtectedRoute allowedRoles={['STUDENT']}>
              <StudentDashboard />
            </ProtectedRoute>
          } />
          <Route path="/student/attendance" element={
            <ProtectedRoute allowedRoles={['STUDENT']}>
              <StudentAttendance />
            </ProtectedRoute>
          } />
          <Route path="/student/profile" element={
            <ProtectedRoute allowedRoles={['STUDENT']}>
              <StudentProfile />
            </ProtectedRoute>
          } />
          <Route path="/student/register-face" element={
            <ProtectedRoute allowedRoles={['STUDENT']}>
              <StudentFaceRegister />
            </ProtectedRoute>
          } />

          {/* Default Route */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
        </Router>
      </AuthProvider>
    </ToastProvider>
  );
}

export default App;
