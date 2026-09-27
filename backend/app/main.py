from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import submissions, pipeline, chat, auth

app = FastAPI(title="MedRAG CRM API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(submissions.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}