import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import AuthLayout from '../components/AuthLayout.jsx';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      await login(email, password);
      navigate('/intake');
    } catch (err) {
      setError(err.message.includes('401') ? 'Invalid email or password.' : 'Something went wrong. Try again.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthLayout title="Welcome back" subtitle="Sign in to continue to MedRAG CRM">
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <Field label="Email">
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@hospital.org" />
        </Field>
        <Field label="Password">
          <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
        </Field>

        {error && <div style={{ color: 'var(--danger)', fontSize: 12.5 }}>{error}</div>}

        <button className="btn btn-primary" type="submit" disabled={busy} style={{ justifyContent: 'center', marginTop: 4 }}>
          {busy ? 'Signing in…' : 'Sign in'}
        </button>
      </form>

      <div style={{ textAlign: 'center', fontSize: 12.5, color: 'var(--ink-faint)', marginTop: 20 }}>
        Don't have an account? <Link to="/signup" style={{ color: 'var(--grad-blue-2)', fontWeight: 700, textDecoration: 'none' }}>Create one</Link>
      </div>
    </AuthLayout>
  );
}

export function Field({ label, children }) {
  return (
    <div>
      <label style={{ fontSize: 12.5, fontWeight: 700, display: 'block', marginBottom: 7 }}>{label}</label>
      <div className="auth-field">{children}</div>
    </div>
  );
}
