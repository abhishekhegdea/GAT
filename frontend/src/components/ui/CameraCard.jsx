import React, { useRef } from 'react';
import Webcam from 'react-webcam';
import Card from './Card';

const CameraCard = ({ onCapture }) => {
  const ref = useRef(null);
  const capture = () => {
    const imageSrc = ref.current.getScreenshot();
    onCapture && onCapture(imageSrc);
  };

  return (
    <Card className="p-4">
      <div className="text-white font-semibold mb-3">Live Camera</div>
      <Webcam audio={false} ref={ref} screenshotFormat="image/jpeg" videoConstraints={{ facingMode: 'user' }} className="rounded-xl" />
      <div className="mt-3 flex justify-end">
        <button className="btn-primary" onClick={capture}>Capture</button>
      </div>
    </Card>
  );
};

export default CameraCard;
