import React, { useState, useEffect, useRef } from 'react';
import Layout from '../../components/Layout';
import { attendanceAPI, studentAPI } from '../../services/api';
import Webcam from 'react-webcam';

const StudentAttendance = () => {
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState(null);
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1); // 1: Select Class, 2: Get Location, 3: Capture Face
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const webcamRef = useRef(null);

  useEffect(() => {
    loadClasses();
  }, []);

  const loadClasses = async () => {
    try {
      const response = await studentAPI.getEnrolledClasses();
      setClasses(response.data.classes);
    } catch (error) {
      setError('Error loading classes');
    }
  };

  const handleSelectClass = async (classId) => {
    setError('');
    setMessage('');
    
    const cls = classes.find(c => c.id === classId);
    setSelectedClass(cls);
    
    // Check eligibility
    try {
      const response = await attendanceAPI.checkEligibility(classId);
      if (response.data.eligible) {
        setStep(2);
        setMessage('Class selected. Please enable location access.');
      } else {
        setError(response.data.reason);
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Error checking eligibility');
    }
  };

  const getLocation = () => {
    setLoading(true);
    setMessage('Getting your location...');
    
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const coords = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        };
        setLocation(coords);
        
        // Validate location
        try {
          const response = await attendanceAPI.validateLocation({
            class_id: selectedClass.id,
            ...coords,
          });
          
          if (response.data.is_valid) {
            setMessage(`Location verified! Distance: ${response.data.distance.toFixed(2)}m`);
            setStep(3);
          } else {
            setError(`You are outside the attendance radius. Distance: ${response.data.distance.toFixed(2)}m`);
          }
        } catch (error) {
          setError('Error validating location');
        }
        setLoading(false);
      },
      (error) => {
        setError('Unable to get location. Please enable location services.');
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  };

  const captureFace = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    
    if (!imageSrc) {
      setError('Please allow camera access');
      return;
    }

    setLoading(true);
    setMessage('Verifying face...');

    try {
      // Convert base64 to blob
      const blob = await fetch(imageSrc).then(r => r.blob());
      
      // Create form data
      const formData = new FormData();
      formData.append('class_id', selectedClass.id);
      formData.append('latitude', location.latitude);
      formData.append('longitude', location.longitude);
      formData.append('image', blob, 'face.jpg');

      const response = await attendanceAPI.markAttendance(formData);
      
      setMessage('✅ Attendance marked successfully!');
      setError('');
      
      // Reset after 3 seconds
      setTimeout(() => {
        setStep(1);
        setSelectedClass(null);
        setLocation(null);
        setMessage('');
      }, 3000);
      
    } catch (error) {
      setError(error.response?.data?.error || 'Error marking attendance');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Mark Attendance">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Progress Indicator */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <StepIndicator number={1} label="Select Class" active={step >= 1} completed={step > 1} />
            <div className="flex-1 h-1 bg-gray-200 mx-2">
              <div className={`h-full ${step > 1 ? 'bg-blue-600' : 'bg-gray-200'} transition-all`} />
            </div>
            <StepIndicator number={2} label="Location" active={step >= 2} completed={step > 2} />
            <div className="flex-1 h-1 bg-gray-200 mx-2">
              <div className={`h-full ${step > 2 ? 'bg-blue-600' : 'bg-gray-200'} transition-all`} />
            </div>
            <StepIndicator number={3} label="Face Verify" active={step >= 3} completed={false} />
          </div>
        </div>

        {/* Messages */}
        {message && (
          <div className="card bg-blue-50 border border-blue-200">
            <p className="text-blue-800">{message}</p>
          </div>
        )}

        {error && (
          <div className="card bg-red-50 border border-red-200">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Step 1: Select Class */}
        {step === 1 && (
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Select Class</h2>
            {classes.length === 0 ? (
              <p className="text-gray-600">You are not enrolled in any classes.</p>
            ) : (
              <div className="space-y-3">
                {classes.map((cls) => (
                  <button
                    key={cls.id}
                    onClick={() => handleSelectClass(cls.id)}
                    className="w-full p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all text-left"
                  >
                    <h3 className="font-semibold text-lg">{cls.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      Time: {cls.start_time} - {cls.end_time}
                    </p>
                    <p className="text-sm text-gray-600">
                      Radius: {cls.radius}m
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Step 2: Get Location */}
        {step === 2 && (
          <div className="card text-center">
            <div className="text-6xl mb-4">📍</div>
            <h2 className="text-xl font-bold mb-4">Enable Location Access</h2>
            <p className="text-gray-600 mb-6">
              We need to verify that you are within {selectedClass?.radius}m of the class location.
            </p>
            <button
              onClick={getLocation}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Getting Location...' : 'Get My Location'}
            </button>
          </div>
        )}

        {/* Step 3: Capture Face */}
        {step === 3 && (
          <div className="card">
            <h2 className="text-xl font-bold mb-4 text-center">Face Verification</h2>
            <div className="mb-4">
              <Webcam
                ref={webcamRef}
                audio={false}
                screenshotFormat="image/jpeg"
                className="w-full rounded-lg"
                videoConstraints={{
                  facingMode: 'user',
                  width: 640,
                  height: 480,
                }}
              />
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-4">
                Position your face in the camera and click capture
              </p>
              <button
                onClick={captureFace}
                disabled={loading}
                className="btn-primary"
              >
                {loading ? 'Verifying...' : 'Capture & Submit'}
              </button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

const StepIndicator = ({ number, label, active, completed }) => {
  return (
    <div className="flex flex-col items-center">
      <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
        completed ? 'bg-blue-600 text-white' :
        active ? 'bg-blue-600 text-white' :
        'bg-gray-200 text-gray-600'
      }`}>
        {completed ? '✓' : number}
      </div>
      <span className="text-xs mt-1 text-gray-600">{label}</span>
    </div>
  );
};

export default StudentAttendance;
