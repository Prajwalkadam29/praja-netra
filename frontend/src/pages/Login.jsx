import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { ShieldCheck, User as UserIcon, Lock, Globe } from 'lucide-react';

const Login = () => {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [isInternal, setIsInternal] = useState(false);
  const [credentials, setCredentials] = useState({ email: '', password: '' });

  const handleInternalLogin = async (e) => {
    e.preventDefault();
    console.log("Sending Login Attempt:", credentials);
    try {
      const response = await api.post('/auth/login/internal', {
        email: credentials.email,
        password: credentials.password
      });

      // 1. Extract data from the successful 200 OK response
      const { user, access_token } = response.data;
      console.log("Login Successful! User Role:", user.role);

      // 2. Update the AuthContext (This saves the token to localStorage)
      login(user, access_token);

      // 3. Redirect based on role
      if (user.role === 'SUPER_ADMIN') {
        navigate('/admin-dashboard');
      } else if (user.role === 'OFFICIAL') {
        navigate('/official-dashboard');
      } else {
        navigate('/citizen-dashboard');
      }

    } catch (err) {
      console.error("Login Error Response:", err.response?.data);
      alert(`Access Denied: ${err.response?.data?.detail || "Invalid Credentials"}`);
    }
  };

    // Inside the Login component, before the return statement
    const handleGoogleLogin = async () => {
      try {
        // 1. In production, this token comes from the Google SDK
        // For your current test setup, we use the bypass token
        const response = await api.post('/auth/login/google', { token: "TEST_TOKEN" });

        const { user, access_token } = response.data;
        console.log("Google Login Successful:", user.email);

        // 2. Update Context and navigate
        login(user, access_token);
        navigate('/citizen-dashboard');

      } catch (err) {
        console.error("Google Auth Failed:", err);
        alert("Google Authentication failed. Please try again.");
      }
    };

  return (
    <div className="min-h-screen bg-[#050a15] flex items-center justify-center p-6 font-sans">
      <div className="w-full max-w-[440px] bg-white dark:bg-white/[0.03] backdrop-blur-2xl border border-white/10 rounded-[2.5rem] p-10 shadow-2xl">
        <header className="text-center mb-10">
          <div className="flex justify-center mb-4">
             <div className="p-3 bg-blue-500/10 rounded-2xl border border-blue-500/20">
                <Globe className="text-blue-400" size={32} />
             </div>
          </div>
          <h1 className="text-4xl font-bold text-white tracking-tighter">Prajā-Netra</h1>
          <p className="text-gray-500 text-sm mt-2 font-medium uppercase tracking-widest">
            {isInternal ? "Official/Admin Entry" : "Citizen Public Portal"}
          </p>
        </header>

        {isInternal ? (
          <form onSubmit={handleInternalLogin} className="space-y-4">
            <div className="relative group">
              <UserIcon className="absolute left-4 top-4 text-gray-500 group-focus-within:text-blue-400" size={18} />
              <input
                type="email" placeholder="Official ID / Email" required
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-4 outline-none focus:border-blue-500 text-white transition-all"
                onChange={e => setCredentials({...credentials, email: e.target.value})}
              />
            </div>
            <div className="relative group">
              <Lock className="absolute left-4 top-4 text-gray-500 group-focus-within:text-blue-400" size={18} />
              <input
                type="password" placeholder="Secure Password" required
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-4 outline-none focus:border-blue-500 text-white transition-all"
                onChange={e => setCredentials({...credentials, password: e.target.value})}
              />
            </div>
            <button className="w-full bg-blue-600 hover:bg-blue-500 py-4 rounded-2xl font-bold text-white transition-all shadow-xl shadow-blue-900/20">
              Sign In to System
            </button>
          </form>
        ) : (
          <div className="space-y-6">
            <button
              onClick={handleGoogleLogin} // Restore this call
              className="w-full flex items-center justify-center gap-3 bg-white text-gray-950 py-4 rounded-2xl font-bold hover:bg-gray-100 transition-all shadow-[0_10px_30px_rgba(0,0,0,0.3)]"
            >
              <img src="https://www.svgrepo.com/show/475656/google-color.svg" className="w-5 h-5" alt="" />
              Sign in with Google
            </button>
            <p className="text-center text-[11px] text-gray-600 px-4">
               By continuing, you agree to report civic issues transparently via the decentralized ledger.
            </p>
          </div>
        )}

        <div className="mt-8 pt-6 border-t border-white/5">
          <button
            onClick={() => setIsInternal(!isInternal)}
            className="w-full text-gray-500 text-[10px] font-black uppercase tracking-widest hover:text-white flex items-center justify-center gap-2 transition-colors"
          >
            <ShieldCheck size={14} className={isInternal ? "text-gray-500" : "text-blue-500"} />
            {isInternal ? "Switch to Citizen Access" : "Official Authorized Login"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;