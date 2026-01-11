import React, { useContext } from 'react';
import { NavLink } from 'react-router-dom';
import { ThemeContext } from '../context/ThemeContext';
import { AuthContext } from '../context/AuthContext';
import { LayoutDashboard, Map, FilePlus, Sun, Moon, LogOut, ShieldCheck, BarChart3 } from 'lucide-react';

const Sidebar = () => {
    const { theme, toggleTheme } = useContext(ThemeContext);
  const { user, logout } = useContext(AuthContext);

  const citizenLinks = [
    { to: "/citizen-dashboard", label: "Dashboard", icon: <LayoutDashboard size={20}/> },
    { to: "/submit-complaint", label: "New Report", icon: <FilePlus size={20}/> },
    { to: "/public-map", label: "Live Map", icon: <Map size={20}/> },
  ];

  const officialLinks = [
    { to: "/official-dashboard", label: "Case Queue", icon: <ShieldCheck size={20}/> },
    { to: "/public-map", label: "City Heatmap", icon: <Map size={20}/> },
  ];

  const adminLinks = [
    { to: "/admin-dashboard", label: "Analytics", icon: <BarChart3 size={20}/> },
    { to: "/public-map", label: "Global Map", icon: <Map size={20}/> },
  ];

  const links = user?.role === 'SUPER_ADMIN' ? adminLinks :
                user?.role === 'OFFICIAL' ? officialLinks : citizenLinks;

  return (
    <div className="w-64 min-h-screen bg-[#0a0f1d] border-r border-white/5 flex flex-col p-6 sticky top-0">
      <div className="mb-10 px-2">
        <h1 className="text-xl font-bold text-white tracking-tighter italic">Prajā-Netra</h1>
        <p className="text-[10px] text-blue-500 font-bold uppercase tracking-widest mt-1">Integrity Portal</p>
      </div>

      <nav className="flex-1 space-y-2">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                isActive ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' : 'text-gray-500 hover:text-white hover:bg-white/5'
              }`
            }
          >
            {link.icon}
            <span className="font-medium text-sm">{link.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Theme Toggle Button */}
      <button onClick={toggleTheme} className="p-2 rounded-lg bg-gray-200 dark:bg-white/10 text-gray-600 dark:text-gray-300">
  {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
</button>

      <button
        onClick={logout}
        className="flex items-center gap-3 px-4 py-3 text-red-400 hover:bg-red-400/10 rounded-xl transition-all"
      >
        <LogOut size={20}/>
        <span className="font-medium text-sm">Sign Out</span>
      </button>
    </div>
  );
};

export default Sidebar;