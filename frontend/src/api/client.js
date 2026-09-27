const BASE = '/api';

function authHeader() {
  const token = localStorage.getItem('medrag_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...authHeader(), ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
}

export const api = {
  // ---- Auth ----
  register: (name, email, password, staffId, role) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify({ name, email, password, staff_id: staffId, role }) }),

  login: (email, password) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),

  me: () => request('/auth/me'),

  logout: () => request('/auth/logout', { method: 'POST' }),

  // Submit files + notes as multipart form data; returns { submission_id }
  createSubmission: (formData) =>
    fetch(`${BASE}/submissions`, { method: 'POST', headers: { ...authHeader() }, body: formData }).then((r) => r.json()),

  // Poll pipeline status for a submission_id
  getPipelineStatus: (submissionId) => request(`/pipeline/status/${submissionId}`),

  // Re-run the pipeline for a submission
  rerunPipeline: (submissionId) =>
    request(`/pipeline/rerun/${submissionId}`, { method: 'POST' }),

  // Send a chat query scoped to a submission/session
  sendMessage: (sessionId, message) =>
    request(`/query`, {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, message }),
    }),

  // List chat sessions
  listSessions: () => request('/sessions'),

  // Real message history for a session — used to reload the chat instead of resetting it
  getMessages: (sessionId) => request(`/sessions/${sessionId}/messages`),
};