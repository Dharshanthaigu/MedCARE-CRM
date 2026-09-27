# MedRAG CRM

A healthcare CRM scaffold connecting document intake → a 5-stage RAG pipeline →
an agentic chatbot, built on a React frontend and a Python (FastAPI) backend.

This is a **working scaffold**, not a finished product: the pipeline and chat
endpoints currently return simulated data so you can see the full UI flow
end-to-end. Swap the stub logic in `backend/app/services/` for real
ingestion, embeddings, a vector store, and an LLM/MCP call, and everything
above it (routers, frontend, polling, chat UI) keeps working unchanged.

## Structure

```
medrag-crm/
├── frontend/                 React + Vite
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx           Shell: sidebar + router
│       ├── theme.css         Design tokens (colors, type, radii)
│       ├── pages/
│       │   ├── Intake.jsx    Page 1 — submission form
│       │   ├── Pipeline.jsx  Page 2 — 5-stage status, polls backend
│       │   └── Chat.jsx      Page 3 — Ask MedRAG chatbot
│       ├── components/
│       │   └── KpiCard.jsx
│       └── api/
│           └── client.js     fetch wrapper for all backend calls
│
└── backend/                  Python + FastAPI
    ├── requirements.txt
    └── app/
        ├── main.py           App entrypoint, CORS, router wiring
        ├── routers/
        │   ├── submissions.py   POST /api/submissions
        │   ├── pipeline.py      GET /api/pipeline/status/{id}, POST /rerun/{id}
        │   └── chat.py          POST /api/query, GET /api/sessions
        ├── services/
        │   ├── rag_pipeline.py  5-stage pipeline runner (stub — replace)
        │   └── chat_service.py  Retrieval + LLM call (stub — replace)
        └── models/
            └── schemas.py       Pydantic request/response models
```

## Running it locally

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend** (in a separate terminal)
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the Vite dev server proxies `/api/*` to the
FastAPI backend on port 8000 (see `vite.config.js`).

## Wiring in the real RAG pipeline

`backend/app/services/rag_pipeline.py` currently simulates the 5 stages with
`asyncio.sleep`. Replace each stage with real work, e.g.:

1. **Ingest & validate** — file type checks, virus scan, size limits
2. **Parse & OCR** — `pypdf` for text PDFs, `pytesseract` or a vision OCR API for scans/images
3. **Chunk & embed** — a text splitter (e.g. LangChain's `RecursiveCharacterTextSplitter`) + an embedding model
4. **Index vectors** — upsert into Chroma, Pinecone, pgvector, or your vector store of choice
5. **LLM ready check** — run a smoke-test retrieval + LLM call against the new index

Keep `stages_done` / `active_stage` updated on the shared state object as
each stage completes — the frontend polls `GET /api/pipeline/status/{id}`
every 1.5s and re-renders the stage cards and donut/progress bar from those
two fields alone.

## Wiring in the chatbot (RAG + MCP + agentic)

`backend/app/services/chat_service.py` is where a real query should:

1. Embed the incoming message with the same embedding model used at ingest
2. Retrieve top-k chunks for the session's submission from the vector store
3. Optionally call MCP tools for agentic steps (e.g. a lab-trend lookup tool)
4. Call your LLM (Claude via the Anthropic API, or any other model) with the
   retrieved chunks + tool outputs as context, and ask it to answer with
   citations
5. Return `{ answer, sources, tool_calls }` — the frontend already renders
   the citation chips and tool-call indicators from this shape

## Sign up / sign in flow

The app is now gated behind auth: visiting any URL while logged out redirects
to `/login`. The pathway is:

```
/signup  →  create account  →  redirected straight into /intake
/login   →  sign in          →  redirected straight into /intake
```

No landing page in between — successful sign-up or sign-in drops the user
directly onto the New Submission page, matching how the rest of the flow
(intake → pipeline → chat) already works.

**Backend** — `app/routers/auth.py` + `app/services/auth_service.py`:
- `POST /api/auth/register` — `{ name, email, password }` → `{ token, user }`
- `POST /api/auth/login` — `{ email, password }` → `{ token, user }`
- `GET /api/auth/me` — returns the current user for a valid `Authorization: Bearer <token>` header
- `POST /api/auth/logout` — invalidates the token

This is an **in-memory stub** (users and tokens live in a Python dict and
reset when the server restarts) so you can see the whole flow work
immediately. Before shipping, replace:
- the password hashing in `auth_service.py` with `passlib[bcrypt]` or `argon2-cffi`
- the in-memory `_USERS` / `_TOKENS` dicts with a real database (Postgres, etc.)
- the random token with a signed, expiring JWT (`python-jose`)

**Frontend** — `src/context/AuthContext.jsx` holds the current user and
token (stored in `localStorage`), exposes `login()`, `register()`, and
`logout()`. `src/components/ProtectedRoute.jsx` wraps the three app pages
and redirects to `/login` if there's no valid session. `src/pages/Login.jsx`
and `Signup.jsx` are the two auth screens, styled with the same design
tokens as the rest of the app.

## Design tokens

`frontend/src/theme.css` holds the full color/typography system used across
all three pages (navy sidebar, violet/blue/teal/pink gradient KPI cards,
pastel tile cards) — reuse these CSS variables for any new page so the UI
stays consistent.
