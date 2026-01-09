import React, { useState, useRef } from 'react';
import Layout from '../../components/Layout';
import { studentAPI } from '../../services/api';
import Webcam from 'react-webcam';
import { useNavigate } from 'react-router-dom';

const StudentFaceRegister = () => {
  const [step, setStep] = useState(1); // 1: Instructions, 2: Capture
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const webcamRef = useRef(null);
  const navigate = useNavigate();

  const captureFace = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    
    if (!imageSrc) {
      setError('Please allow camera access');
      return;
    }

    setLoading(true);
    setMessage('Processing...');
    setError('');

    try {
      // Convert base64 to blob
      const blob = await fetch(imageSrc).then(r => r.blob());
      
      // Create form data
      const formData = new FormData();
      formData.append('image', blob, 'face.jpg');

      await studentAPI.registerFace(formData);
      
      setMessage('✅ Face registered successfully!');
      
      // Redirect after 2 seconds
      setTimeout(() => {
        navigate('/student');
      }, 2000);
      
    } catch (error) {
      setError(error.response?.data?.error || 'Error registering face');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Register Face">
      <div className="max-w-2xl mx-auto space-y-6">
        {message && (
          <div className="card bg-green-50 border border-green-200">
            <p className="text-green-800 text-center font-semibold">{message}</p>
          </div>
        )}

        {error && (
          <div className="card bg-red-50 border border-red-200">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {step === 1 && (
          <div className="card">
            <h2 className="text-2xl font-bold mb-4">Face Registration Instructions</h2>
            
            <div className="space-y-4 mb-6">
              <div className="flex items-start">
                <span className="text-2xl mr-3">💡</span>
                <div>
                  <h3 className="font-semibold">Good Lighting</h3>
                  <p className="text-sm text-gray-600">Ensure you are in a well-lit area</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <span className="text-2xl mr-3">😊</span>
                <div>
                  <h3 className="font-semibold">Face the Camera</h3>
                  <p className="text-sm text-gray-600">Look directly at the camera with a neutral expression</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <span className="text-2xl mr-3">👓</span>
                <div>
                  <h3 className="font-semibold">Remove Accessories</h3>
                  <p className="text-sm text-gray-600">Remove sunglasses, hats, or masks</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <span className="text-2xl mr-3">👤</span>
                <div>
                  <h3 className="font-semibold">Solo Photo</h3>
                  <p className="text-sm text-gray-600">Ensure only your face is visible in the frame</p>
                </div>
              </div>
            </div>

            <button
              onClick={() => setStep(2)}
              className="btn-primary w-full"
            >
              Continue to Camera
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="card">
            <h2 className="text-xl font-bold mb-4 text-center">Capture Your Face</h2>
            
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

            <div className="text-center space-y-3">
              <p className="text-sm text-gray-600">
                Position your face in the center and click capture when ready
              </p>
              
              <div className="flex space-x-3">
                <button
                  onClick={captureFace}
                  disabled={loading}
                  className="btn-primary flex-1"
                >
                  {loading ? 'Processing...' : '📸 Capture Face'}
                </button>
                
                <button
                  onClick={() => setStep(1)}
                  disabled={loading}
                  className="btn-secondary flex-1"
                >
                  Back
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default StudentFaceRegister;
