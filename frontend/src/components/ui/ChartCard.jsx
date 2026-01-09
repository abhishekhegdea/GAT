import React from 'react';
import Card from './Card';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const ChartCard = ({ title, data }) => {
  return (
    <Card className="p-5">
      <div className="text-white font-semibold mb-3">{title}</div>
      <div style={{ width: '100%', height: 240 }}>
        <ResponsiveContainer>
          <LineChart data={data}>
            <XAxis dataKey="name" stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
            <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
            <Tooltip contentStyle={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff', backdropFilter: 'blur(8px)' }} />
            <Line type="monotone" dataKey="value" stroke="#00E5FF" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};

export default ChartCard;
