import React from 'react';

const ProgressRing = ({ progress = 0, size = 120, stroke = 8, color = '#00E5FF' }) => {
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progress / 100) * circumference;
  return (
    <svg width={size} height={size}>
      <circle stroke="#1F3C88" fill="transparent" strokeWidth={stroke} r={radius} cx={size/2} cy={size/2}/>
      <circle stroke={color} fill="transparent" strokeWidth={stroke} r={radius} cx={size/2} cy={size/2}
        strokeDasharray={`${circumference} ${circumference}`} strokeDashoffset={offset} style={{ transition: 'stroke-dashoffset 0.35s' }} />
    </svg>
  );
};

export default ProgressRing;
