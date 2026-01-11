import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Send, FileUp, MapPin, X, Loader2, Music } from 'lucide-react';
import api from '../api/axios';
import { useNavigate } from 'react-router-dom';

const CreateComplaint = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [files, setFiles] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    complaint_type: 'others',
    location: '',
  });

  // Handle Text Changes
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle File Selection
  const onFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles([...files, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  // Fetch Browser Location
  const detectLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        setFormData({ ...formData, location: `Lat: ${pos.coords.latitude}, Lng: ${pos.coords.longitude}` });
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // 1. Create the base complaint
      const { data } = await api.post('/complaints/', formData);

      // 2. Upload each file as evidence
      for (const file of files) {
        const fileData = new FormData();
        fileData.append('file', file);
        await api.post(`/complaints/${data.id}/evidence`, fileData);
      }

      // 3. Trigger AI Analysis
      await api.post(`/complaints/${data.id}/analyze`);

      navigate('/citizen-dashboard');
    } catch (err) {
      alert("Error submitting complaint. Check console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050a15] text-white p-6 flex flex-col items-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-2xl bg-white/[0.03] backdrop-blur-3xl border border-white/10 rounded-[2.5rem] p-10 mt-10 shadow-2xl"
      >
        <header className="mb-10 text-center">
          <h1 className="text-3xl font-bold mb-2">File a Report</h1>
          <p className="text-gray-500 text-sm italic">Secure, encrypted, and anchored on blockchain.</p>
        </header>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Voice Input Trigger */}
          <div className="flex flex-col items-center p-6 bg-blue-500/5 rounded-3xl border border-blue-500/10">
            <motion.button
              type="button"
              whileTap={{ scale: 0.9 }}
              onClick={() => setIsRecording(!isRecording)}
              className={`p-6 rounded-full transition-all ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-blue-600 hover:bg-blue-500 shadow-lg shadow-blue-600/20'}`}
            >
              {isRecording ? <Music size={24} /> : <Mic size={24} />}
            </motion.button>
            <p className="mt-4 text-xs font-bold text-blue-400 uppercase tracking-widest">
              {isRecording ? "Listening..." : "Tap to record voice report"}
            </p>
          </div>

          <div className="space-y-4">
            <input
              name="title"
              placeholder="Case Title"
              className="w-full bg-white/[0.05] border border-white/10 rounded-2xl py-4 px-6 focus:border-blue-500 outline-none transition-all"
              onChange={handleChange}
              required
            />

            <textarea
              name="description"
              placeholder="Describe the issue in detail..."
              rows="4"
              className="w-full bg-white/[0.05] border border-white/10 rounded-2xl py-4 px-6 focus:border-blue-500 outline-none transition-all resize-none"
              onChange={handleChange}
              required
            />

            <div className="flex gap-4">
                <div className="flex-1 relative">
                    <input
                        name="location"
                        value={formData.location}
                        placeholder="Location"
                        className="w-full bg-white/[0.05] border border-white/10 rounded-2xl py-4 px-6 outline-none"
                        onChange={handleChange}
                    />
                    <button type="button" onClick={detectLocation} className="absolute right-4 top-1/2 -translate-y-1/2 text-blue-400 hover:text-blue-300">
                        <MapPin size={20} />
                    </button>
                </div>
            </div>
          </div>

          {/* Multi-File Upload Area */}
          <div className="bg-white/[0.02] border-2 border-dashed border-white/10 rounded-3xl p-8 text-center relative">
            <input type="file" multiple onChange={onFileChange} className="absolute inset-0 opacity-0 cursor-pointer" />
            <FileUp className="mx-auto text-gray-600 mb-2" />
            <p className="text-gray-500 text-sm">Drop images or documents as evidence</p>
          </div>

          {/* File Preview List */}
          <div className="flex flex-wrap gap-3">
            <AnimatePresence>
                {files.map((file, i) => (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        key={i}
                        className="bg-blue-500/10 border border-blue-500/20 px-4 py-2 rounded-xl flex items-center gap-2 text-xs"
                    >
                        <span className="max-w-[100px] truncate">{file.name}</span>
                        <X size={14} className="cursor-pointer" onClick={() => removeFile(i)} />
                    </motion.div>
                ))}
            </AnimatePresence>
          </div>

          <button
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 py-5 rounded-2xl font-bold flex items-center justify-center gap-2 transition-all shadow-xl shadow-blue-600/10"
          >
            {loading ? <Loader2 className="animate-spin" /> : <><Send size={18} /> Seal Case on Blockchain</>}
          </button>
        </form>
      </motion.div>
    </div>
  );
};

export default CreateComplaint;