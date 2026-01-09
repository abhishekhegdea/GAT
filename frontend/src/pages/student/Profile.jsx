import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { studentAPI } from '../../services/api';

const StudentProfile = () => {
  const [profile, setProfile] = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const [profileRes, attendanceRes] = await Promise.all([
        studentAPI.getProfile(),
        studentAPI.getAttendanceHistory({ per_page: 10 }),
      ]);
      setProfile(profileRes.data.profile);
      setAttendance(attendanceRes.data.attendance);
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout title="My Profile">
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="My Profile">
      <div className="space-y-6">
        {/* Profile Information */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Profile Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-gray-600">Full Name</label>
              <p className="font-semibold">{profile?.full_name}</p>
            </div>
            <div>
              <label className="text-sm text-gray-600">Email</label>
              <p className="font-semibold">{profile?.email}</p>
            </div>
            <div>
              <label className="text-sm text-gray-600">Student ID</label>
              <p className="font-semibold">{profile?.student_id || '-'}</p>
            </div>
            <div>
              <label className="text-sm text-gray-600">Phone</label>
              <p className="font-semibold">{profile?.phone || '-'}</p>
            </div>
            <div>
              <label className="text-sm text-gray-600">Face Registered</label>
              <p>
                <span className={`badge ${profile?.has_face_registered ? 'badge-success' : 'badge-warning'}`}>
                  {profile?.has_face_registered ? 'Yes' : 'No'}
                </span>
              </p>
            </div>
            <div>
              <label className="text-sm text-gray-600">Account Status</label>
              <p>
                <span className={`badge ${profile?.is_active ? 'badge-success' : 'badge-danger'}`}>
                  {profile?.is_active ? 'Active' : 'Inactive'}
                </span>
              </p>
            </div>
          </div>
        </div>

        {/* Recent Attendance */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Recent Attendance</h2>
          {attendance.length === 0 ? (
            <p className="text-gray-600">No attendance records yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Class</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {attendance.map((record) => (
                    <tr key={record.id}>
                      <td className="px-4 py-3 text-sm">{record.class_name}</td>
                      <td className="px-4 py-3 text-sm">
                        {new Date(record.timestamp).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        {new Date(record.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`badge ${
                          record.status === 'PRESENT' ? 'badge-success' :
                          record.status === 'LATE' ? 'badge-warning' :
                          'badge-danger'
                        }`}>
                          {record.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default StudentProfile;
