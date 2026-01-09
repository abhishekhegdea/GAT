import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { teacherAPI } from '../../services/api';

const TeacherAttendance = () => {
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState('');
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadClasses();
  }, []);

  const loadClasses = async () => {
    try {
      const response = await teacherAPI.getMyClasses();
      setClasses(response.data.classes);
    } catch (error) {
      alert('Error loading classes');
    }
  };

  const loadAttendance = async (classId) => {
    setLoading(true);
    try {
      const response = await teacherAPI.getClassAttendance(classId);
      setAttendance(response.data.attendance);
    } catch (error) {
      alert('Error loading attendance');
    } finally {
      setLoading(false);
    }
  };

  const handleClassChange = (classId) => {
    setSelectedClass(classId);
    if (classId) {
      loadAttendance(classId);
    } else {
      setAttendance([]);
    }
  };

  const handleExport = async () => {
    if (!selectedClass) {
      alert('Please select a class first');
      return;
    }

    try {
      const response = await teacherAPI.exportClassAttendance(selectedClass);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `attendance_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('Error exporting attendance');
    }
  };

  return (
    <Layout title="Class Attendance">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">View Attendance</h2>
          {selectedClass && (
            <button onClick={handleExport} className="btn-primary">
              📥 Export to CSV
            </button>
          )}
        </div>

        {/* Class Selector */}
        <div className="card">
          <label className="block text-sm font-medium mb-2">Select Class</label>
          <select
            value={selectedClass}
            onChange={(e) => handleClassChange(e.target.value)}
            className="input-field max-w-md"
          >
            <option value="">-- Select a class --</option>
            {classes.map((cls) => (
              <option key={cls.id} value={cls.id}>
                {cls.name} ({cls.start_time} - {cls.end_time})
              </option>
            ))}
          </select>
        </div>

        {/* Attendance Table */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : attendance.length === 0 ? (
          selectedClass && (
            <div className="card text-center py-12">
              <p className="text-gray-600">No attendance records for this class</p>
            </div>
          )
        ) : (
          <div className="card overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Distance</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Face Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {attendance.map((record) => (
                  <tr key={record.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{record.student_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(record.timestamp).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(record.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {record.distance?.toFixed(2)}m
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
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

export default TeacherAttendance;
