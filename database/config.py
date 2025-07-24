import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Garante que a raiz do projeto está no sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dikas_orlando.db")

print(f"Conectando ao banco de dados: {DATABASE_URL.split('@')[0].split('://')}")

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    """
    Cria todas as tabelas no banco de dados.
    Importe todos os modelos aqui para garantir que serão registrados no metadata.
    """
    from database.models.user_model import User
    from database.models.message_model import Message
    from database.models.conversation_context import ConversationContext
    from database.models.context_message import ContextMessage
    from database.models.context_document import ContextDocument
    # Importe outros modelos se existirem
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """
    Obtém uma sessão de banco de dados.
    Deve ser usado em um contexto 'with'.
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()