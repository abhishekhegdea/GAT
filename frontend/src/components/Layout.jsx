import React from 'react';
import { useAuth } from '../context/AuthContext';
import Navbar from './ui/Navbar';
import Sidebar from './ui/Sidebar';

const Layout = ({ children, title }) => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-deepBlue via-brand-indigo to-gray-900">
      <div className="sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Navbar />
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex gap-6">
        <Sidebar />
        <main className="flex-1 glass p-6">
          {title && (
            <div className="page-title">{title}</div>
          )}
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
