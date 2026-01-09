import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import Card from '../../components/ui/Card';
import Modal from '../../components/ui/Modal';
import CameraCard from '../../components/ui/CameraCard';
import ProgressRing from '../../components/ui/ProgressRing';
import { useToast } from '../../components/ui/Toast';
import { Camera, MapPin, CheckCircle, Clock, AlertCircle, Download } from 'lucide-react';
import { studentAPI } from '../../services/api';

const StudentDashboard = () => {
  const { notify } = useToast();
  const [attendanceData, setAttendanceData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCamera, setShowCamera] = useState(false);
  const [gpsStatus, setGpsStatus] = useState('idle'); // idle, loading, success, error
  const [attendanceStatus, setAttendanceStatus] = useState('idle');
  const [currentLocation, setCurrentLocation] = useState(null);

  useEffect(() => {
    loadAttendance();
  }, []);

  const loadAttendance = async () => {
    try {
      const response = await studentAPI.getMyAttendance();
      setAttendanceData(response.data.attendance || []);
    } catch (error) {
      console.error('Error loading attendance:', error);
      notify('Failed to load attendance', 'error');
    } finally {
      setLoading(false);
    }
  };

  const getGPS = () => {
    setGpsStatus('loading');
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy
          });
          setGpsStatus('success');
          notify('Location acquired', 'success');
        },
        (error) => {
          setGpsStatus('error');
          notify('Could not get location', 'error');
        }
      );
    } else {
      setGpsStatus('error');
      notify('Geolocation not supported', 'error');
    }
  };

  const markAttendance = async () => {
    if (!currentLocation) {
      notify('Please enable GPS first', 'error');
      return;
    }

    setAttendanceStatus('loading');
    try {
      const response = await studentAPI.markAttendance({
        latitude: currentLocation.lat,
        longitude: currentLocation.lng,
        accuracy: currentLocation.accuracy
      });
      
      if (response.status === 'success') {
        setAttendanceStatus('success');
        notify('Attendance marked successfully!', 'success');
        setShowCamera(false);
        setTimeout(() => setAttendanceStatus('idle'), 3000);
      }
    } catch (error) {
      setAttendanceStatus('error');
      notify('Failed to mark attendance', 'error');
    }
  };

  if (loading) {
    return (
      <Layout title="Student Dashboard">
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-cyan"></div>
        </div>
      </Layout>
    );
  }

  const attendanceCount = attendanceData.length;
  const attendancePercentage = 85; // Sample percentage

  return (
    <Layout title="Student Dashboard">
      <div className="space-y-6">
        {/* Welcome Card */}
        <Card className="p-6 bg-gradient-to-r from-brand-indigo/20 to-brand-cyan/10">
          <div className="text-white">
            <div className="text-2xl font-bold">Welcome, Student</div>
            <div className="text-gray-300 text-sm mt-1">Mark your attendance and track your progress</div>
          </div>
        </Card>

        {/* Mark Attendance CTA */}
        <Card className="p-6 bg-gradient-to-r from-brand-softPurple/20 to-brand-cyan/20 border border-brand-cyan/30">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-white font-bold text-lg">Ready to Mark Attendance?</div>
              <div className="text-gray-300 text-sm mt-1">Enable GPS and capture your face to mark attendance</div>
            </div>
            <button
              onClick={getGPS}
              className="btn-primary flex items-center gap-2 whitespace-nowrap"
            >
              <MapPin size={18} /> Enable GPS
            </button>
          </div>
          
          {currentLocation && (
            <div className="mt-4 p-3 bg-brand-deepBlue/50 rounded-lg border border-brand-cyan/30">
              <div className="text-xs text-gray-300">
                📍 Location: {currentLocation.lat.toFixed(4)}°, {currentLocation.lng.toFixed(4)}°
              </div>
              <div className="text-xs text-gray-400 mt-1">
                Accuracy: ±{currentLocation.accuracy.toFixed(0)}m
              </div>
            </div>
          )}
        </Card>

        {/* GPS & Attendance Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* GPS Status Card */}
          <Card className="p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="text-white font-semibold">GPS Status</div>
              {gpsStatus === 'success' && <CheckCircle size={20} className="text-brand-neonGreen" />}
              {gpsStatus === 'error' && <AlertCircle size={20} className="text-red-500" />}
              {gpsStatus === 'loading' && <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-brand-cyan"></div>}
              {gpsStatus === 'idle' && <MapPin size={20} className="text-gray-500" />}
            </div>
            <div className="text-sm text-gray-300 capitalize">
              {gpsStatus === 'loading' && 'Acquiring location...'}
              {gpsStatus === 'success' && 'Location acquired'}
              {gpsStatus === 'error' && 'Location failed'}
              {gpsStatus === 'idle' && 'Click Enable GPS'}
            </div>
          </Card>

          {/* Camera Status Card */}
          <Card className="p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="text-white font-semibold">Camera</div>
              {currentLocation && (
                <button
                  onClick={() => setShowCamera(true)}
                  className="btn-primary text-xs py-1 px-3 flex items-center gap-1"
                >
                  <Camera size={14} /> Open
                </button>
              )}
            </div>
            <div className="text-sm text-gray-300">
              {currentLocation ? 'Ready to capture' : 'Enable GPS first'}
            </div>
          </Card>
        </div>

        {/* Attendance Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Total Attendance */}
          <Card className="p-6 flex flex-col items-center text-center">
            <div className="text-3xl font-bold text-white mb-2">{attendanceCount}</div>
            <div className="text-gray-400 text-sm">Total Attendance</div>
          </Card>

          {/* Attendance Percentage */}
          <Card className="p-6 flex flex-col items-center justify-center">
            <ProgressRing percentage={attendancePercentage} size={80} />
            <div className="text-white font-bold mt-2">{attendancePercentage}%</div>
            <div className="text-gray-400 text-sm">Attendance Rate</div>
          </Card>

          {/* Last Marked */}
          <Card className="p-6 flex flex-col">
            <div className="flex items-center gap-2 mb-3">
              <Clock size={18} className="text-brand-cyan" />
              <div className="text-gray-400 text-sm">Last Marked</div>
            </div>
            <div className="text-white font-bold">
              {attendanceData.length > 0 
                ? new Date(attendanceData[0]?.timestamp).toLocaleDateString()
                : 'Not yet marked'
              }
            </div>
          </Card>
        </div>

        {/* Attendance History */}
        <Card className="p-6">
          <div className="text-white font-bold text-lg mb-4 flex items-center gap-2">
            <Clock size={20} /> Attendance History
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-2 px-3 text-gray-300 font-medium">Date</th>
                  <th className="text-left py-2 px-3 text-gray-300 font-medium">Time</th>
                  <th className="text-left py-2 px-3 text-gray-300 font-medium">Class</th>
                  <th className="text-left py-2 px-3 text-gray-300 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {attendanceData.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="py-4 px-3 text-center text-gray-400">
                      No attendance records yet
                    </td>
                  </tr>
                ) : (
                  attendanceData.map((record, idx) => (
                    <tr key={idx} className="border-b border-white/5 hover:bg-white/5">
                      <td className="py-3 px-3 text-gray-100">
                        {new Date(record.timestamp).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-3 text-gray-300">
                        {new Date(record.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="py-3 px-3 text-gray-300">{record.class_name || 'Class'}</td>
                      <td className="py-3 px-3">
                        <span className="badge badge-success">Present</span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {attendanceData.length > 0 && (
            <button className="btn-secondary flex items-center gap-2 mt-4">
              <Download size={16} /> Export History
            </button>
          )}
        </Card>

        {/* Camera Modal */}
        <Modal
          open={showCamera}
          title="Mark Attendance"
          onClose={() => setShowCamera(false)}
          onConfirm={markAttendance}
          confirmText="Mark Attendance"
          confirmDisabled={attendanceStatus === 'loading'}
        >
          <div className="space-y-4">
            <CameraCard />
            <div className="p-3 bg-brand-deepBlue/50 rounded-lg border border-brand-cyan/30">
              <div className="text-xs text-gray-300 flex items-center gap-2">
                <CheckCircle size={14} className="text-brand-neonGreen" />
                GPS Location verified
              </div>
              <div className="text-xs text-gray-400 mt-1">
                Ready to capture your face and mark attendance
              </div>
            </div>
          </div>
        </Modal>
      </div>
    </Layout>
  );
};

export default StudentDashboard;
