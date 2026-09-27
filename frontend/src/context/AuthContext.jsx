import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../api/client.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On load, if a token exists, verify it and restore the session
  useEffect(() => {
    const token = localStorage.getItem('medrag_token');
    if (!token) {
      setLoading(false);
      return;
    }
    api.me()
      .then(setUser)
      .catch(() => localStorage.removeItem('medrag_token'))
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password) {
    const { token, user } = await api.login(email, password);
    localStorage.setItem('medrag_token', token);
    setUser(user);
  }

  async function register(name, email, password, staffId, role) {
    const { token, user } = await api.register(name, email, password, staffId, role);
    localStorage.setItem('medrag_token', token);
    setUser(user);
  }

  async function logout() {
    try { await api.logout(); } catch { /* ignore */ }
    localStorage.removeItem('medrag_token');
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}