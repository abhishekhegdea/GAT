import React, { useEffect, useState } from 'react';
import Card from './Card';

const KPICard = ({ label, value, icon }) => {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    const target = Number(value) || 0;
    let start = 0;
    const step = Math.ceil(target / 60);
    const id = setInterval(() => {
      start += step;
      if (start >= target) { setDisplay(target); clearInterval(id); }
      else setDisplay(start);
    }, 16);
    return () => clearInterval(id);
  }, [value]);

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-gray-300">{label}</div>
          <div className="text-2xl font-bold text-white">{display.toLocaleString()}</div>
        </div>
        {icon && <div className="text-brand-cyan">{icon}</div>}
      </div>
    </Card>
  );
};

export default KPICard;
