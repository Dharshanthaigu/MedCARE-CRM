import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import AuthLayout from '../components/AuthLayout.jsx';
import { Field } from './Login.jsx';

export default function Signup() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [staffId, setStaffId] = useState('');
  const [role, setRole] = useState('Doctor / Staff');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setBusy(true);
    try {
      await register(name, email, password, staffId, role);
      navigate('/intake');
    } catch (err) {
      setError(err.message.includes('400') ? 'An account with this email already exists.' : 'Something went wrong. Try again.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthLayout title="Create your account" subtitle="Set up access to MedRAG CRM">
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <Field label="Full name">
          <input required value={name} onChange={(e) => setName(e.target.value)} placeholder="Dr. S. Nair" />
        </Field>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <Field label="Hospital Staff ID">
            <input required value={staffId} onChange={(e) => setStaffId(e.target.value)} placeholder="e.g. HSP-00214" />
          </Field>
          <Field label="Role">
            <select value={role} onChange={(e) => setRole(e.target.value)} className="auth-select" required>
              <option>Admin</option>
              <option>Chief Nurse</option>
              <option>Doctor / Staff</option>
            </select>
          </Field>
        </div>
        <Field label="Email">
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@hospital.org" />
        </Field>
        <Field label="Password">
          <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" />
        </Field>
        <Field label="Confirm password">
          <input type="password" required value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Re-enter your password" />
        </Field>

        {error && <div style={{ color: 'var(--danger)', fontSize: 12.5 }}>{error}</div>}

        <button className="btn btn-primary" type="submit" disabled={busy} style={{ justifyContent: 'center', marginTop: 4 }}>
          {busy ? 'Creating account…' : 'Create account'}
        </button>
      </form>

      <div style={{ textAlign: 'center', fontSize: 12.5, color: 'var(--ink-faint)', marginTop: 20 }}>
        Already have an account? <Link to="/login" style={{ color: 'var(--grad-blue-2)', fontWeight: 700, textDecoration: 'none' }}>Sign in</Link>
      </div>
    </AuthLayout>
  );
}    