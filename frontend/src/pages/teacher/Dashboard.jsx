import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import Card from '../../components/ui/Card';
import Modal from '../../components/ui/Modal';
import MapPicker from '../../components/ui/MapPicker';
import { useToast } from '../../components/ui/Toast';
import { Lock, Download, MapPin, Users, BookOpen } from 'lucide-react';
import { teacherAPI } from '../../services/api';

const TeacherDashboard = () => {
  const { notify } = useToast();
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedClass, setSelectedClass] = useState(null);
  const [showMap, setShowMap] = useState(false);

  useEffect(() => {
    loadClasses();
  }, []);

  const loadClasses = async () => {
    try {
      const response = await teacherAPI.getMyClasses();
      setClasses(response.data.classes || []);
    } catch (error) {
      console.error('Error loading classes:', error);
      notify('Failed to load classes', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout title="Teacher Dashboard">
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-cyan"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Teacher Dashboard">
      <div className="space-y-6">
        {/* Welcome Card */}
        <Card className="p-6 bg-gradient-to-r from-brand-indigo/20 to-brand-cyan/10">
          <div className="text-white">
            <div className="text-2xl font-bold">Welcome back, Teacher</div>
            <div className="text-gray-300 text-sm mt-1">Manage classes, set locations, and track attendance</div>
          </div>
        </Card>

        {/* Classes Grid */}
        <div>
          <div className="text-white font-bold text-xl mb-4 flex items-center gap-2">
            <BookOpen size={24} /> Your Classes
          </div>
          {classes.length === 0 ? (
            <Card className="p-8 text-center">
              <div className="text-gray-400">No classes assigned</div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {classes.map((cls) => (
                <Card key={cls.id} className="p-4 hover:shadow-glass transition-all group cursor-pointer"
                  onClick={() => setSelectedClass(cls)}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <div className="text-white font-semibold group-hover:text-brand-cyan transition">{cls.name || cls.title}</div>
                      <div className="text-xs text-gray-400">{cls.class_code || 'N/A'}</div>
                    </div>
                    <span className="badge badge-success">Active</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-gray-300">
                      <Users size={14} />
                      <span>{cls.student_count || 0} Students</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <MapPin size={14} />
                      <span>Radius: {cls.radius || 150}m</span>
                    </div>
                  </div>
                  <button className="btn-secondary w-full text-xs py-2 mt-4 flex items-center justify-center gap-2"
                    onClick={(e) => { e.stopPropagation(); setSelectedClass(cls); setShowMap(true); }}
                  >
                    <MapPin size={14} /> Edit Location
                  </button>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Attendance Table */}
        {selectedClass && (
          <Card className="p-6">
            <div className="text-white font-bold text-lg mb-4">Live Attendance - {selectedClass.name || selectedClass.title}</div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-2 px-3 text-gray-300 font-medium">Student Name</th>
                    <th className="text-left py-2 px-3 text-gray-300 font-medium">Time</th>
                    <th className="text-left py-2 px-3 text-gray-300 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-3 px-3 text-gray-100">Sample Student</td>
                    <td className="py-3 px-3 text-gray-300">09:15 AM</td>
                    <td className="py-3 px-3">
                      <span className="badge badge-success">Present</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="flex gap-3 mt-4">
              <button className="btn-primary flex items-center gap-2" onClick={() => notify('Attendance locked', 'success')}>
                <Lock size={16} /> Lock Attendance
              </button>
              <button className="btn-secondary flex items-center gap-2" onClick={() => notify('Exporting...', 'info')}>
                <Download size={16} /> Export
              </button>
            </div>
          </Card>
        )}

        {/* Map Modal */}
        <Modal
          open={showMap}
          title={`Set Location - ${selectedClass?.name || selectedClass?.title}`}
          onClose={() => setShowMap(false)}
          onConfirm={() => { notify('Location updated', 'success'); setShowMap(false); }}
          confirmText="Save Location"
        >
          {selectedClass && <MapPicker onChange={() => {}} />}
        </Modal>
      </div>
    </Layout>
  );
};

export default TeacherDashboard;
