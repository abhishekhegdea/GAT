import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Users, Settings, ListChecks, School, UserCircle, Camera, MapPin, FileDown } from 'lucide-react';

const items = [
  { to: '/admin', label: 'Admin Dashboard', icon: <Home size={18} /> },
  { to: '/admin/users', label: 'Users', icon: <Users size={18} /> },
  { to: '/admin/settings', label: 'Settings', icon: <Settings size={18} /> },
  { to: '/admin/attendance', label: 'Attendance', icon: <ListChecks size={18} /> },
  { to: '/admin/logs', label: 'Audit Logs', icon: <ListChecks size={18} /> },
  { to: '/teacher', label: 'Teacher Dashboard', icon: <School size={18} /> },
  { to: '/teacher/classes', label: 'Classes', icon: <ListChecks size={18} /> },
  { to: '/teacher/attendance', label: 'Live Attendance', icon: <ListChecks size={18} /> },
  { to: '/student', label: 'Student Dashboard', icon: <UserCircle size={18} /> },
  { to: '/student/register-face', label: 'Register Face', icon: <Camera size={18} /> },
  { to: '/student/attendance', label: 'Mark Attendance', icon: <MapPin size={18} /> },
  { to: '/admin/export', label: 'Export', icon: <FileDown size={18} /> },
];

const Sidebar = () => {
  return (
    <aside className="sidebar">
      <nav className="flex flex-col gap-1">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `flex items-center gap-2 px-3 py-2 rounded-xl transition-all ${isActive ? 'bg-white/15 text-white' : 'text-gray-300 hover:text-white hover:bg-white/10'}`}
          >
            {item.icon}
            <span className="text-sm">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
