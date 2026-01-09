import React, { useEffect, useState } from 'react';
import { Sun, Moon } from 'lucide-react';

const ThemeToggle = () => {
  const [dark, setDark] = useState(() => localStorage.getItem('theme') === 'dark');

  useEffect(() => {
    const root = document.documentElement;
    if (dark) {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [dark]);

  return (
    <button
      aria-label="Toggle theme"
      onClick={() => setDark(!dark)}
      className="btn-secondary flex items-center gap-2"
    >
      {dark ? <Sun size={18} /> : <Moon size={18} />}
      <span>{dark ? 'Light' : 'Dark'} Mode</span>
    </button>
  );
};

export default ThemeToggle;
