import React, { useEffect, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom'; // 1. Import useNavigate
import { motion } from 'framer-motion';
import {
  Plus,
  CheckCircle2,
  Clock,
  AlertCircle,
  TrendingUp,
  MapPin,
  ThumbsUp
} from 'lucide-react';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axios';

const CitizenDashboard = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate(); // 2. Initialize navigate
  const [complaints, setComplaints] = useState([]);
  const [stats, setStats] = useState({ total: 0, resolved: 0, pending: 0, impact: 0 });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch User's complaints
        const response = await api.get('/complaints/');
        setComplaints(response.data);

        // Calculate basic stats locally for now
        const resolved = response.data.filter(c => c.status === 'resolved').length;
        const pending = response.data.length - resolved;
        setStats({
          total: response.data.length,
          resolved,
          pending,
          impact: response.data.reduce((acc, curr) => acc + (curr.severity_score || 0), 0) * 10
        });
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      }
    };
    fetchDashboardData();
  }, []);

  return (
    <div className="min-h-screen bg-[#050a15] text-white font-sans p-6 lg:p-10">

      {/* Navbar Section */}
      <nav className="flex justify-between items-center mb-12">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Citizen Portal</h2>
          <p className="text-gray-500 text-sm">Welcome back, {user?.full_name || 'Citizen'}</p>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/submit-complaint')}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl transition-all font-semibold shadow-lg shadow-blue-900/20"
          >
            <Plus size={18} /> New Complaint
          </button>
          <button onClick={logout} className="text-gray-500 hover:text-white text-sm font-medium">Logout</button>
        </div>
      </nav>

      {/* Stats Ribbon */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        {[
          { label: 'Impact Score', value: stats.impact, icon: TrendingUp, color: 'text-blue-400', bg: 'bg-blue-400/10' },
          { label: 'Active Reports', value: stats.pending, icon: Clock, color: 'text-orange-400', bg: 'bg-orange-400/10' },
          { label: 'Resolved', value: stats.resolved, icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
          { label: 'Integrity Points', value: stats.total * 5, icon: ThumbsUp, color: 'text-purple-400', bg: 'bg-purple-400/10' },
        ].map((stat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-white/[0.03] border border-white/10 p-6 rounded-3xl"
          >
            <div className={`w-10 h-10 ${stat.bg} ${stat.color} rounded-xl flex items-center justify-center mb-4`}>
              <stat.icon size={20} />
            </div>
            <p className="text-gray-500 text-xs uppercase tracking-widest font-bold mb-1">{stat.label}</p>
            <h3 className="text-3xl font-semibold">{stat.value}</h3>
          </motion.div>
        ))}
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">

        {/* Recent Personal Complaints */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex justify-between items-center px-2">
            <h3 className="text-xl font-bold">My Recent Reports</h3>
            <span className="text-blue-400 text-sm cursor-pointer hover:underline">View all</span>
          </div>

          {complaints.length === 0 ? (
            <div className="bg-white/[0.02] border border-dashed border-white/10 rounded-3xl p-20 text-center">
              <AlertCircle className="mx-auto text-gray-700 mb-4" size={40} />
              <p className="text-gray-500">No complaints filed yet. Your voice matters!</p>
            </div>
          ) : (
            complaints.map((complaint, i) => (
              <motion.div
                key={complaint.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="group bg-white/[0.03] hover:bg-white/[0.05] border border-white/10 p-6 rounded-3xl transition-all cursor-pointer"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-lg font-semibold group-hover:text-blue-400 transition-colors">{complaint.title}</h4>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                      <span className="flex items-center gap-1"><MapPin size={12}/> {complaint.location}</span>
                      <span>Filed on: {new Date(complaint.filed_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    complaint.status === 'resolved' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-orange-500/10 text-orange-400'
                  }`}>
                    {complaint.status}
                  </span>
                </div>
                <p className="text-gray-400 text-sm line-clamp-2 leading-relaxed">
                  {complaint.description}
                </p>
              </motion.div>
            ))
          )}
        </div>

        {/* Community Activity / Sidebar */}
        <div className="space-y-6">
          <h3 className="text-xl font-bold px-2">Global Hotspots</h3>
          <div className="bg-gradient-to-br from-blue-600/20 to-indigo-900/10 border border-white/10 rounded-[2.5rem] p-8">
            <p className="text-sm text-blue-200/70 mb-6 leading-relaxed">
              We've noticed a cluster of water-related issues in <span className="text-white font-bold">Baner</span>.
              Is your issue related?
            </p>
            <button
              onClick={() => navigate('/public-map')}
              className="w-full bg-white/10 hover:bg-white/20 text-white text-sm font-semibold py-3 rounded-2xl transition-all">
              View Live Map
            </button>
          </div>

          <div className="bg-white/[0.02] border border-white/5 rounded-[2rem] p-6">
            <h4 className="text-sm font-bold text-gray-400 mb-4 uppercase tracking-widest">System Integrity</h4>
            <div className="space-y-4">
               <div className="flex items-center gap-3 text-xs text-gray-500">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                  Blockchain Node: Online
               </div>
               <div className="flex items-center gap-3 text-xs text-gray-500">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                  AI Analysis Engine: Active
               </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CitizenDashboard;