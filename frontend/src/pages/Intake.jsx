import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import KpiCard from '../components/KpiCard.jsx';
import { api } from '../api/client.js';

export default function Intake() {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [notes, setNotes] = useState('');
  const [patientId, setPatientId] = useState('PT-48213');
  const [department, setDepartment] = useState('Internal Medicine');
  const [submitting, setSubmitting] = useState(false);

  const totalSize = files.reduce((s, f) => s + f.size, 0) / 1024 / 1024;
  const canSubmit = (files.length > 0 || notes.length > 0) && !submitting;

  function onFilesSelected(e) {
    setFiles((prev) => [...prev, ...Array.from(e.target.files)]);
  }

  function removeFile(idx) {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  }

  async function handleSubmit() {
    setSubmitting(true);
    try {
      const formData = new FormData();
      files.forEach((f) => formData.append('files', f));
      formData.append('notes', notes);
      formData.append('patient_id', patientId);
      formData.append('department', department);

      const { submission_id } = await api.createSubmission(formData);
      navigate(`/pipeline?submission_id=${submission_id}`);
    } catch (err) {
      console.error('Submission failed', err);
      alert('Submission failed — check the backend is running.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page-body">
      <div className="kpi-row">
        <KpiCard tone="violet" label="Files attached" value={files.length} sub="this submission" />
        <KpiCard tone="blue" label="Total size" value={`${totalSize.toFixed(2)} MB`} sub="under 25MB/file limit" />
        <KpiCard tone="teal" label="Note length" value={notes.length} sub="characters embedded" />
        <KpiCard tone="pink" label="Target index" value="clinical-v3" sub={department} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 22 }}>
        <div>
          <label style={{ fontWeight: 700, fontSize: 12.5, display: 'block', marginBottom: 8 }}>
            Documents &amp; images
          </label>
          <div style={{
            border: '1.5px dashed #C4D3F0', borderRadius: 20, padding: 28, textAlign: 'center',
            background: 'var(--pastel-blue)', cursor: 'pointer'
          }}
            onClick={() => document.getElementById('fileInput').click()}
          >
            <div>Drop files here, or <b>browse</b></div>
            <div style={{ fontSize: 12, color: 'var(--ink-faint)', marginTop: 4 }}>
              PDF, JPG, PNG, DOCX &middot; up to 25MB each
            </div>
            <input id="fileInput" type="file" multiple hidden onChange={onFilesSelected} />
          </div>

          <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
            {files.map((f, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: 10, border: '1px solid var(--border)',
                borderRadius: 10, padding: '9px 11px'
              }}>
                <div style={{ flex: 1, fontSize: 13 }}>{f.name}</div>
                <div style={{ fontSize: 11, color: 'var(--ink-faint)' }}>{(f.size / 1024 / 1024).toFixed(2)} MB</div>
                <button onClick={() => removeFile(i)} style={{ border: 'none', background: 'none' }}>✕</button>
              </div>
            ))}
          </div>

          <label style={{ fontWeight: 700, fontSize: 12.5, display: 'block', margin: '20px 0 8px' }}>
            Clinical notes / free text
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Paste or type a sentence, paragraph, or clinical summary…"
            style={{ width: '100%', minHeight: 90, borderRadius: 10, border: '1px solid var(--border)', padding: 10 }}
          />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 16 }}>
            <div>
              <label style={{ fontWeight: 700, fontSize: 12.5, display: 'block', marginBottom: 8 }}>Patient reference ID</label>
              <input value={patientId} onChange={(e) => setPatientId(e.target.value)} style={{ width: '100%', padding: 10, borderRadius: 10, border: '1px solid var(--border)' }} />
            </div>
            <div>
              <label style={{ fontWeight: 700, fontSize: 12.5, display: 'block', marginBottom: 8 }}>Department</label>
              <select value={department} onChange={(e) => setDepartment(e.target.value)} style={{ width: '100%', padding: 10, borderRadius: 10, border: '1px solid var(--border)' }}>
                <option>Cardiology</option>
                <option>Internal Medicine</option>
                <option>Radiology</option>
                <option>Oncology</option>
              </select>
            </div>
          </div>
        </div>

        <div className="card" style={{ padding: 20 }}>
          <h3 style={{ fontSize: 15, marginBottom: 14 }}>Submission summary</h3>
          <SummaryRow k="Files attached" v={files.length} />
          <SummaryRow k="Total size" v={`${totalSize.toFixed(2)} MB`} />
          <SummaryRow k="Free-text notes" v={`${notes.length} chars`} />
          <SummaryRow k="Destination index" v="clinical-rag-v3" />
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: 16 }} disabled={!canSubmit} onClick={handleSubmit}>
            {submitting ? 'Submitting…' : 'Submit & start processing'}
          </button>
        </div>
      </div>
    </div>
  );
}

function SummaryRow({ k, v }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)', fontSize: 13 }}>
      <span style={{ color: 'var(--ink-soft)' }}>{k}</span>
      <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{v}</span>
    </div>
  );
}
