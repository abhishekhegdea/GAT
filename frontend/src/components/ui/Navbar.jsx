import React from 'react';
import { useAuth } from '../../context/AuthContext';
import ThemeToggle from './ThemeToggle';
import { ShieldCheck, MapPin } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <div className="glass px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <ShieldCheck className="text-brand-cyan" />
        <div>
          <div className="neon-title text-xl">GeoFace Attendance</div>
          <div className="text-xs text-gray-300 flex items-center gap-1"><MapPin size={14}/> Secure • Location • Face</div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <ThemeToggle />
        {user && (
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-300">{user.full_name} ({user.role})</span>
            <button className="btn-secondary" onClick={logout}>Logout</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Navbar;
