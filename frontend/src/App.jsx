import React from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import Login from './pages/Login.jsx';
import Signup from './pages/Signup.jsx';
import Intake from './pages/Intake.jsx';
import Pipeline from './pages/Pipeline.jsx';
import Chat from './pages/Chat.jsx';
import './App.css';

const navItems = [
  { to: '/intake', label: 'New submission' },
  { to: '/pipeline', label: 'Pipeline status' },
  { to: '/chat', label: 'Ask MedRAG' },
];

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Protected app routes — everything below requires a logged-in user */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppShell />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

function AppShell() {
  const { user, logout } = useAuth();

  return (
    <div className="shell">
      <aside className="rail">
        <div className="rail-brand">
          <div className="mark">M</div>
          <span>MedRAG</span>
        </div>
        <div className="rail-section-label">RAG pipeline</div>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => 'nav-item' + (isActive ? ' active' : '')}
          >
            {item.label}
          </NavLink>
        ))}
        <div className="rail-footer">
          <div className="avatar">{initials(user?.name)}</div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="who">{user?.name || 'Signed in'}</div>
            <div className="role">{user?.role} &middot; {user?.staff_id}</div>
          </div>
          <button
            onClick={logout}
            title="Sign out"
            style={{ border: 'none', background: 'none', color: 'var(--sidebar-ink-dim)', cursor: 'pointer', fontSize: 11 }}
          >
            Sign out
          </button>
        </div>
      </aside>

      <main className="main">
        <Routes>
          <Route path="/" element={<Navigate to="/intake" replace />} />
          <Route path="/intake" element={<Intake />} />
          <Route path="/pipeline" element={<Pipeline />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </main>
    </div>
  );
}

function initials(name) {
  if (!name) return '?';
  return name.split(' ').map((p) => p[0]).slice(0, 2).join('').toUpperCase();
}