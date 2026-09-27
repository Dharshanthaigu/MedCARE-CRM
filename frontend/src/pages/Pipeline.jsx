import React, { useEffect, useState, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import KpiCard from '../components/KpiCard.jsx';
import { api } from '../api/client.js';

const STAGE_LABELS = [
  { title: 'Ingest & validate', desc: 'Checks file integrity, type, and virus scan.' },
  { title: 'Parse & OCR', desc: 'Extracts text from PDFs and scanned images.' },
  { title: 'Chunk & embed', desc: 'Splits content, generates embeddings.' },
  { title: 'Index vectors', desc: 'Writes embeddings to the vector store.' },
  { title: 'LLM ready check', desc: 'Runs a smoke-test query on the new index.' },
];

export default function Pipeline() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const submissionId = params.get('submission_id') || 'demo';
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  const poll = useCallback(async () => {
    try {
      const data = await api.getPipelineStatus(submissionId);
      setStatus(data);
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    }
  }, [submissionId]);

  useEffect(() => {
    let interval;
    poll().then((data) => {
      // Poll every 1.5s until all 5 stages are done
      interval = setInterval(async () => {
        const d = await poll();
        if (d && d.stages_done >= 5) clearInterval(interval);
      }, 1500);
    });
    return () => clearInterval(interval);
  }, [poll]);

  const stagesDone = status?.stages_done ?? 0;
  const activeStage = status?.active_stage ?? null;
  const ready = stagesDone >= 5;

  return (
    <div className="page-body">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 18 }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--ink-faint)' }}>
          submission_ref: {submissionId}
        </div>
        <button className="btn btn-ghost" onClick={() => api.rerunPipeline(submissionId).then(poll)}>
          Re-run
        </button>
      </div>

      <div className="kpi-row">
        <KpiCard tone="violet" label="Stages complete" value={`${stagesDone}/5`} sub="live status" />
        <KpiCard tone="blue" label="Chunks embedded" value={status?.chunks ?? '—'} sub="1536-dim vectors" />
        <KpiCard tone="teal" label="OCR confidence" value={status?.ocr_confidence ? `${status.ocr_confidence}%` : '—'} sub="avg across scans" />
        <KpiCard tone="pink" label="Avg retrieval" value={status?.avg_latency_ms ? `${status.avg_latency_ms}ms` : '—'} sub="smoke-test query" />
      </div>

      {error && <div style={{ color: 'var(--danger)', marginBottom: 12 }}>Backend error: {error}</div>}

      <div style={{ height: 9, borderRadius: 5, background: 'var(--surface-alt)', marginBottom: 20, overflow: 'hidden' }}>
        <div style={{
          height: '100%', width: `${(stagesDone / 5) * 100}%`,
          background: 'linear-gradient(90deg, var(--grad-violet-1), var(--grad-blue-2))',
          transition: 'width .5s ease'
        }} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12 }}>
        {STAGE_LABELS.map((stage, i) => {
          const stageNum = i + 1;
          const isDone = stageNum <= stagesDone;
          const isActive = stageNum === activeStage;
          return (
            <div key={i} className="card" style={{
              padding: '15px 13px',
              background: isDone ? 'var(--pastel-green)' : isActive ? 'var(--pastel-violet)' : 'var(--surface-alt)',
              border: 'none'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 9 }}>
                <span style={{
                  width: 25, height: 25, borderRadius: '50%', display: 'flex', alignItems: 'center',
                  justifyContent: 'center', fontSize: 11.5, fontWeight: 700, fontFamily: 'var(--font-mono)',
                  background: isDone ? 'var(--success)' : isActive ? 'var(--grad-violet-2)' : 'var(--surface)',
                  color: isDone || isActive ? '#fff' : 'var(--ink-faint)'
                }}>{stageNum}</span>
                <span style={{ fontSize: 10, fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                  {isDone ? 'Done' : isActive ? 'Processing' : 'Waiting'}
                </span>
              </div>
              <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 4 }}>{stage.title}</div>
              <div style={{ fontSize: 11.5, color: 'var(--ink-soft)' }}>{stage.desc}</div>
            </div>
          );
        })}
      </div>

      {ready && (
        <div className="card" style={{
          marginTop: 22, padding: '20px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          background: 'linear-gradient(120deg, var(--pastel-violet), var(--pastel-blue))'
        }}>
          <div>
            <div style={{ fontWeight: 700, fontFamily: 'var(--font-display)' }}>
              Index ready — {status.chunks} chunks
            </div>
            <div style={{ fontSize: 12, color: 'var(--ink-soft)', fontFamily: 'var(--font-mono)' }}>
              clinical-rag-v3 &middot; avg. retrieval latency {status.avg_latency_ms}ms
            </div>
          </div>
          <button className="btn btn-primary" onClick={() => navigate(`/chat?session_id=${submissionId}`)}>
            Open chatbot
          </button>
        </div>
      )}
    </div>
  );
}
