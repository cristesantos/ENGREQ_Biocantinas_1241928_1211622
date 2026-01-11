from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
from pathlib import Path

# Caminho para o banco de dados: d:\ENGREQ\ENGREQ_Biocantinas_1241928_1211622\biocantinas.db
# Path: backend/app/db/session.py (4 níveis acima = projeto raiz)
PROJECT_ROOT = Path(__file__).resolve().parents[4]  
DEFAULT_DB_PATH = PROJECT_ROOT / "biocantinas.db"

# Se a BD padrão não existe na raiz, usa a do script
if not DEFAULT_DB_PATH.exists():
    SCRIPT_DB_PATH = PROJECT_ROOT / "scripts" / "biocantinas.db"
    if SCRIPT_DB_PATH.exists():
        DEFAULT_DB_PATH = SCRIPT_DB_PATH

DB_PATH = os.getenv("BIOCANTINAS_DB_PATH", f"sqlite:///{DEFAULT_DB_PATH}")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False} if DB_PATH.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Ensure tables exist
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
