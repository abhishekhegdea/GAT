import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { adminAPI } from '../../services/api';

const AdminAttendance = () => {
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAttendance();
  }, []);

  const loadAttendance = async () => {
    try {
      const response = await adminAPI.getAllAttendance();
      setAttendance(response.data.attendance);
    } catch (error) {
      alert('Error loading attendance');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (confirm('Delete this attendance record?')) {
      try {
        await adminAPI.deleteAttendance(id);
        alert('Attendance deleted');
        loadAttendance();
      } catch (error) {
        alert('Error deleting attendance');
      }
    }
  };

  const handleExport = async () => {
    try {
      const response = await adminAPI.exportAttendance({});
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `attendance_export_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('Error exporting attendance');
    }
  };

  return (
    <Layout title="Attendance Management">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">All Attendance Records</h2>
          <button onClick={handleExport} className="btn-primary">
            📥 Export to CSV
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="card overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Class</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date/Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Distance</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Face Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {attendance.map((record) => (
                  <tr key={record.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{record.student_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{record.class_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {new Date(record.timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{record.distance?.toFixed(2)}m</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {record.face_match_score ? (record.face_match_score * 100).toFixed(1) + '%' : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`badge ${
                        record.status === 'PRESENT' ? 'badge-success' :
                        record.status === 'LATE' ? 'badge-warning' :
                        'badge-danger'
                      }`}>
                        {record.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleDelete(record.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default AdminAttendance;
