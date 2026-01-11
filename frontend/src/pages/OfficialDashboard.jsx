import React, { useEffect, useState, useContext } from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, MessageSquare, AlertTriangle, FileText, CheckCircle } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axios';

const OfficialDashboard = () => {
  const { user } = useContext(AuthContext);
  const [complaints, setComplaints] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [note, setNote] = useState("");

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const { data } = await api.get('/official/complaints'); // Assigned cases
        setComplaints(data);
      } catch (err) { console.error(err); }
    };
    fetchCases();
  }, []);

  const updateStatus = async (id, status) => {
    await api.patch(`/official/complaints/${id}/status`, { status });
    setComplaints(complaints.map(c => c.id === id ? { ...c, status } : c));
  };

  const addNote = async (id) => {
    await api.post(`/official/complaints/${id}/notes`, { content: note });
    setNote("");
    alert("Internal Note Added");
  };

  return (
    <div className="min-h-screen bg-[#050a15] text-white flex font-sans">

      {/* Sidebar - Case List */}
      <div className="w-1/3 border-r border-white/10 p-6 overflow-y-auto">
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <ShieldCheck className="text-blue-500" /> Assigned Cases
        </h2>
        <div className="space-y-4">
          {complaints.map((c) => (
            <div
              key={c.id}
              onClick={() => setSelectedCase(c)}
              className={`p-4 rounded-2xl cursor-pointer border transition-all ${
                selectedCase?.id === c.id ? 'bg-blue-600/20 border-blue-500' : 'bg-white/5 border-transparent hover:bg-white/10'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500">ID: #{c.id}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  c.severity_score >= 7 ? 'bg-red-500/20 text-red-400' : 'bg-orange-500/20 text-orange-400'
                }`}>
                  Severity: {c.severity_score}
                </span>
              </div>
              <h4 className="font-semibold text-sm truncate">{c.title}</h4>
            </div>
          ))}
        </div>
      </div>

      {/* Main View - Case Details */}
      <div className="flex-1 p-10 overflow-y-auto">
        {selectedCase ? (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="flex justify-between items-start mb-10">
              <div>
                <h1 className="text-4xl font-bold mb-2">{selectedCase.title}</h1>
                <p className="text-gray-500">Location: {selectedCase.location}</p>
              </div>
              <div className="flex gap-3">
                <button onClick={() => updateStatus(selectedCase.id, 'investigating')} className="bg-orange-600/20 text-orange-400 border border-orange-600/30 px-4 py-2 rounded-xl text-sm font-bold">Investigate</button>
                <button onClick={() => updateStatus(selectedCase.id, 'resolved')} className="bg-emerald-600/20 text-emerald-400 border border-emerald-600/30 px-4 py-2 rounded-xl text-sm font-bold">Mark Resolved</button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-8 mb-10">
              <div className="bg-white/5 p-6 rounded-3xl border border-white/10">
                <h4 className="text-xs font-bold text-blue-400 uppercase tracking-widest mb-4">AI Analysis Summary</h4>
                <p className="text-gray-300 leading-relaxed text-sm">{selectedCase.summary_en || "Analysis pending..."}</p>
              </div>
              <div className="bg-white/5 p-6 rounded-3xl border border-white/10">
                <h4 className="text-xs font-bold text-purple-400 uppercase tracking-widest mb-4">Blockchain Integrity</h4>
                <p className="text-[10px] font-mono text-gray-500 break-all">{selectedCase.blockchain_hash || "Not anchored yet"}</p>
              </div>
            </div>

            {/* Internal Collaboration */}
            <div className="bg-white/5 p-8 rounded-[2.5rem] border border-white/10">
              <h4 className="font-bold flex items-center gap-2 mb-6">
                <MessageSquare size={18} /> Internal Official Notes
              </h4>
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Write an internal note for other officials..."
                className="w-full bg-black/20 border border-white/10 rounded-2xl p-4 text-sm mb-4 outline-none focus:border-blue-500"
              />
              <button onClick={() => addNote(selectedCase.id)} className="bg-blue-600 px-6 py-2 rounded-xl text-sm font-bold">Save Note</button>
            </div>
          </motion.div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-gray-600">
            <FileText size={60} strokeWidth={1} className="mb-4" />
            <p>Select a case from the sidebar to begin investigation</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default OfficialDashboard;