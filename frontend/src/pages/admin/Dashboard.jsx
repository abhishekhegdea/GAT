import React, { useState, useEffect } from 'react';
import Layout from '../../components/Layout';
import KPICard from '../../components/ui/KPICard';
import ChartCard from '../../components/ui/ChartCard';
import { adminAPI } from '../../services/api';

const sampleTrend = [
  { name: 'Mon', value: 120 },
  { name: 'Tue', value: 134 },
  { name: 'Wed', value: 150 },
  { name: 'Thu', value: 148 },
  { name: 'Fri', value: 172 },
  { name: 'Sat', value: 98 },
  { name: 'Sun', value: 65 },
];

const AdminDashboard = () => {
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      const response = await adminAPI.getStatistics();
      setStatistics(response.data.statistics);
    } catch (error) {
      console.error('Error loading statistics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout title="Admin Dashboard">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-cyan"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Admin Dashboard">
      <div className="space-y-6">
        <div className="card p-6">
          <div className="text-white text-xl font-semibold">Welcome, Administrator</div>
          <div className="text-gray-300 text-sm">Monitor users, attendance, and configure system settings.</div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard label="Total Users" value={statistics?.total_users || 0} />
          <KPICard label="Students" value={statistics?.total_students || 0} />
          <KPICard label="Teachers" value={statistics?.total_teachers || 0} />
          <KPICard label="Active Classes" value={statistics?.active_classes || 0} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <ChartCard title="Attendance Trend (7d)" data={sampleTrend} />
          <ChartCard title="Logins (7d)" data={sampleTrend.map((x,i)=>({ name: x.name, value: x.value - i*10 }))} />
        </div>
      </div>
    </Layout>
  );
};

export default AdminDashboard;
