import React, { useContext } from 'react';
import { motion } from 'framer-motion';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';

const Login = () => {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleGoogleLogin = async () => {
  try {
    const response = await api.post('/auth/login/google', { token: "TEST_TOKEN" });
    const { user, access_token } = response.data;

    login(user, access_token);

    // FIX: Match the SUPER_ADMIN role string
    if (user.role === 'SUPER_ADMIN') {
      navigate('/admin-dashboard');
    } else if (user.role === 'OFFICIAL') {
      navigate('/official-dashboard');
    } else {
      navigate('/citizen-dashboard');
    }
  } catch (err) {
    console.error("Login failed", err);
  }
};

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center bg-[#050a15] overflow-hidden">

      {/* Dynamic Background Elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-600/10 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-900/20 blur-[120px]" />
      </div>

      {/* Main Container */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative z-10 w-full max-w-[440px] px-6"
      >
        <div className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 rounded-[2.5rem] p-10 shadow-2xl">

          {/* Header Section */}
          <div className="text-center mb-10">
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-bold tracking-widest uppercase mb-6"
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
              </span>
              Secure Network Access
            </motion.div>

            <h1 className="text-4xl font-semibold tracking-tight text-white mb-3">
              Prajā-Netra
            </h1>
            <p className="text-gray-400 text-sm leading-relaxed">
              Log in to the decentralized governance portal <br/> to report and track civic issues.
            </p>
          </div>

          {/* Action Section */}
          <div className="space-y-4">
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleGoogleLogin}
              className="w-full flex items-center justify-center gap-3 bg-white text-gray-950 font-semibold py-4 px-6 rounded-2xl hover:bg-gray-100 transition-colors shadow-[0_10px_20px_rgba(0,0,0,0.2)]"
            >
              <img src="https://www.svgrepo.com/show/475656/google-color.svg" className="w-5 h-5" alt="Google" />
              Continue with Google
            </motion.button>

            <button className="w-full py-4 text-gray-500 text-sm hover:text-white transition-colors">
              Access Official Dashboard
            </button>
          </div>

          {/* Footer Info */}
          <div className="mt-10 pt-8 border-t border-white/5">
            <div className="flex justify-between items-center text-[10px] text-gray-600 uppercase tracking-[0.2em]">
              <span>Immutable</span>
              <span className="h-1 w-1 bg-gray-700 rounded-full"></span>
              <span>Transparent</span>
              <span className="h-1 w-1 bg-gray-700 rounded-full"></span>
              <span>Accountable</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 z-0 opacity-[0.03] pointer-events-none"
           style={{ backgroundImage: 'radial-gradient(circle, #fff 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
    </div>
  );
};

export default Login;