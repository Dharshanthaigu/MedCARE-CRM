import React from 'react';

export default function AuthLayout({ title, subtitle, children }) {
  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--page-bg)', padding: 20
    }}>
      <div style={{ width: '100%', maxWidth: 400 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, justifyContent: 'center', marginBottom: 28 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 11,
            background: 'linear-gradient(135deg, var(--grad-violet-1), var(--grad-blue-2))',
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 700
          }}>M</div>
          <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 19 }}>MedRAG</span>
        </div>

        <div className="card" style={{ padding: '32px 30px' }}>
          <h2 style={{ fontSize: 20, marginBottom: 4 }}>{title}</h2>
          <p style={{ fontSize: 12.5, color: 'var(--ink-faint)', marginBottom: 26 }}>{subtitle}</p>
          {children}
        </div>

        <p style={{ textAlign: 'center', fontSize: 11, color: 'var(--ink-faint)', marginTop: 18, fontFamily: 'var(--font-mono)' }}>
          clinical-rag-v3 &middot; secure workspace access
        </p>
      </div>
    </div>
  );
}
