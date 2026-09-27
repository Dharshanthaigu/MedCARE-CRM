import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../api/client.js';

const WELCOME = { role: 'ai', text: 'Index is ready. Ask me anything about this submission.', sources: [] };

export default function Chat() {
  const [params] = useSearchParams();
  const sessionId = params.get('session_id') || 'demo';
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoadingHistory(true);
    api.getMessages(sessionId)
      .then((history) => {
        if (cancelled) return;
        if (history && history.length > 0) {
          setMessages(history.map((m) => ({ role: m.role, text: m.content, sources: m.sources || [] })));
        } else {
          setMessages([WELCOME]);
        }
      })
      .catch(() => {
        if (!cancelled) setMessages([WELCOME]);
      })
      .finally(() => {
        if (!cancelled) setLoadingHistory(false);
      });
    return () => { cancelled = true; };
  }, [sessionId]);

  async function send() {
    const text = input.trim();
    if (!text || sending) return;
    setMessages((m) => [...m, { role: 'user', text }]);
    setInput('');
    setSending(true);
    try {
      const res = await api.sendMessage(sessionId, text);
      setMessages((m) => [...m, { role: 'ai', text: res.answer, sources: res.sources || [] }]);
    } catch (err) {
      setMessages((m) => [...m, { role: 'ai', text: `Error contacting backend: ${err.message}`, sources: [] }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="page-body">
      <div className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: 480 }}>
        <div style={{ flex: 1, padding: '22px 24px', display: 'flex', flexDirection: 'column', gap: 16, maxWidth: 720, margin: '0 auto', width: '100%' }}>
          {loadingHistory && (
            <div style={{ fontSize: 12, color: 'var(--ink-faint)', textAlign: 'center' }}>Loading conversation…</div>
          )}
          {messages.map((m, i) => (
            <div key={i} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '86%' }}>
              <div style={{
                padding: '11px 15px', borderRadius: 14, fontSize: 13.5,
                background: m.role === 'user'
                  ? 'linear-gradient(135deg, var(--grad-teal-1), var(--grad-teal-2))'
                  : 'var(--surface-alt)',
                color: m.role === 'user' ? '#fff' : 'var(--ink)',
              }}>
                {m.text}
              </div>
              {m.sources?.length > 0 && (
                <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
                  {m.sources.map((s, j) => (
                    <span key={j} style={{
                      fontSize: 11, background: 'var(--surface)', border: '1px solid var(--border)',
                      borderRadius: 20, padding: '5px 11px'
                    }}>
                      {s.doc} &middot; {s.location}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div style={{ borderTop: '1px solid var(--border)', padding: '14px 18px' }}>
          <div style={{
            maxWidth: 720, margin: '0 auto', display: 'flex', gap: 10, alignItems: 'center',
            background: 'var(--surface-alt)', border: '1px solid var(--border)', borderRadius: 26, padding: '6px 6px 6px 18px'
          }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send()}
              placeholder="Ask about this submission…"
              style={{ flex: 1, border: 'none', background: 'none', outline: 'none', fontSize: 13 }}
            />
            <button
              onClick={send}
              disabled={sending}
              style={{
                width: 34, height: 34, borderRadius: '50%', border: 'none',
                background: 'linear-gradient(135deg, var(--grad-violet-1), var(--grad-blue-2))', color: '#fff'
              }}
            >
              ➤
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}