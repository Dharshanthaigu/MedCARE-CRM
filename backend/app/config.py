import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://medrag:medrag_dev_password@localhost:5432/medrag_crm",
)
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")