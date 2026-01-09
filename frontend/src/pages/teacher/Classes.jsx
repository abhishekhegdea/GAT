import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import { teacherAPI } from '../../services/api';

const TeacherClasses = () => {
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    latitude: '',
    longitude: '',
    radius: 100,
    start_time: '',
    end_time: '',
    is_active: true,
    attendance_enabled: true,
  });

  useEffect(() => {
    loadClasses();
  }, []);

  const loadClasses = async () => {
    try {
      const response = await teacherAPI.getMyClasses();
      setClasses(response.data.classes);
    } catch (error) {
      alert('Error loading classes');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateClass = async (e) => {
    e.preventDefault();
    try {
      await teacherAPI.createClass(formData);
      alert('Class created successfully');
      setShowModal(false);
      setFormData({
        name: '',
        description: '',
        latitude: '',
        longitude: '',
        radius: 100,
        start_time: '',
        end_time: '',
        is_active: true,
        attendance_enabled: true,
      });
      loadClasses();
    } catch (error) {
      alert(error.response?.data?.error || 'Error creating class');
    }
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData({
            ...formData,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
          alert('Location captured!');
        },
        (error) => {
          alert('Unable to get location');
        }
      );
    } else {
      alert('Geolocation is not supported');
    }
  };

  const handleDelete = async (classId) => {
    if (confirm('Are you sure you want to delete this class?')) {
      try {
        await teacherAPI.deleteClass(classId);
        alert('Class deleted');
        loadClasses();
      } catch (error) {
        alert('Error deleting class');
      }
    }
  };

  return (
    <Layout title="My Classes">
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Manage Classes</h2>
          <button onClick={() => setShowModal(true)} className="btn-primary">
            + Create New Class
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : classes.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-600 mb-4">No classes created yet</p>
            <button onClick={() => setShowModal(true)} className="btn-primary">
              Create Your First Class
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {classes.map((cls) => (
              <div key={cls.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold">{cls.name}</h3>
                  <div className="flex space-x-2">
                    <span className={`badge ${cls.is_active ? 'badge-success' : 'badge-danger'}`}>
                      {cls.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>

                <p className="text-gray-600 mb-4">{cls.description || 'No description'}</p>

                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <span className="text-gray-600 w-24">Time:</span>
                    <span className="font-medium">{cls.start_time} - {cls.end_time}</span>
                  </div>
                  <div className="flex items-center">
                    <span className="text-gray-600 w-24">Location:</span>
                    <span className="font-medium">{cls.latitude?.toFixed(4)}, {cls.longitude?.toFixed(4)}</span>
                  </div>
                  <div className="flex items-center">
                    <span className="text-gray-600 w-24">Radius:</span>
                    <span className="font-medium">{cls.radius}m</span>
                  </div>
                  <div className="flex items-center">
                    <span className="text-gray-600 w-24">Attendance:</span>
                    <span className={`badge ${cls.attendance_enabled ? 'badge-success' : 'badge-danger'}`}>
                      {cls.attendance_enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200 flex space-x-2">
                  <button className="btn-secondary flex-1 text-sm">
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(cls.id)}
                    className="btn-danger flex-1 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create Class Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-md w-full p-6 max-h-[90vh] overflow-y-auto">
              <h3 className="text-xl font-bold mb-4">Create New Class</h3>
              <form onSubmit={handleCreateClass} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Class Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="input-field"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="input-field"
                    rows="3"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium mb-1">Start Time</label>
                    <input
                      type="time"
                      value={formData.start_time}
                      onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                      className="input-field"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">End Time</label>
                    <input
                      type="time"
                      value={formData.end_time}
                      onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                      className="input-field"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Class Location</label>
                  <div className="flex space-x-2">
                    <input
                      type="number"
                      step="any"
                      value={formData.latitude}
                      onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                      className="input-field"
                      placeholder="Latitude"
                      required
                    />
                    <input
                      type="number"
                      step="any"
                      value={formData.longitude}
                      onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                      className="input-field"
                      placeholder="Longitude"
                      required
                    />
                  </div>
                  <button
                    type="button"
                    onClick={getCurrentLocation}
                    className="mt-2 text-sm text-blue-600 hover:text-blue-800"
                  >
                    📍 Use Current Location
                  </button>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Attendance Radius (meters)</label>
                  <input
                    type="number"
                    value={formData.radius}
                    onChange={(e) => setFormData({ ...formData, radius: parseInt(e.target.value) })}
                    className="input-field"
                    min="10"
                    max="500"
                    required
                  />
                </div>

                <div className="flex space-x-3">
                  <button type="submit" className="btn-primary flex-1">
                    Create Class
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default TeacherClasses;
