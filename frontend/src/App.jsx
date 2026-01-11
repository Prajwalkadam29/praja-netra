import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import CitizenDashboard from './pages/CitizenDashboard';
import CreateComplaint from './pages/CreateComplaint';
import PublicMap from './pages/PublicMap';
import OfficialDashboard from './pages/OfficialDashboard';
import AdminDashboard from './pages/AdminDashboard'; // Uncomment when you build this
import Sidebar from './components/Sidebar';
import { useContext } from 'react';
import { AuthContext } from './context/AuthContext';


function App() {
  const { user, loading } = useContext(AuthContext);

  if (loading) return null;

  const getLandingPage = () => {
    if (!user) return "/login";
    // FIX: Change ADMIN to SUPER_ADMIN
    if (user.role === 'SUPER_ADMIN') return "/admin-dashboard";
    if (user.role === 'OFFICIAL') return "/official-dashboard";
    return "/citizen-dashboard";
  };

  return (
    <Router>
        <div className="flex">
            {user && <Sidebar />} {/* Only show sidebar if logged in */}
            <main className="flex-1">
      <Routes>
        <Route path="/" element={<Navigate to={getLandingPage()} />} />
        <Route path="/login" element={!user ? <Login /> : <Navigate to={getLandingPage()} />} />

        {/* Protected Routes */}
        <Route path="/citizen-dashboard" element={user?.role === 'CITIZEN' ? <CitizenDashboard /> : <Navigate to="/login" />} />
        <Route path="/official-dashboard" element={user?.role === 'OFFICIAL' ? <OfficialDashboard /> : <Navigate to="/login" />} />

        {/* FIX: Change ADMIN to SUPER_ADMIN */}
        <Route
          path="/admin-dashboard"
          element={user?.role === 'SUPER_ADMIN' ? <AdminDashboard /> : <Navigate to="/login" />}
        />

        <Route path="/submit-complaint" element={user ? <CreateComplaint /> : <Navigate to="/login" />} />
        {/* Global Features accessible to ALL logged-in roles */}
        <Route
          path="/public-map"
          element={user ? <PublicMap /> : <Navigate to="/login" />}
        />
      </Routes>
      </main>
      </div>
    </Router>
  );
}

export default App;