# database/config.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

try:
    from dotenv import load_dotenv
    # Carrega variáveis de ambiente do arquivo .env (se existir)
    load_dotenv()
except ImportError:
    print("Biblioteca python-dotenv não instalada. Ignorando arquivo .env.")

# Carrega a string de conexão do ambiente
# Usa uma conexão SQLite padrão se DATABASE_URL não estiver definida
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dikas_orlando.db")

print(f"Conectando ao banco de dados: {DATABASE_URL.split('@')[0].split('://')}")

# Cria o mecanismo do banco de dados
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
    # Adiciona opções específicas para SQLite se for usado
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Cria a fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria a classe base para todos os modelos
Base = declarative_base()

# Função auxiliar para criar as tabelas
def create_tables():
    """Cria todas as tabelas no banco de dados."""
    # Importar todos os modelos para que sejam incluídos na criação de tabelas
    from database.models import User, Message
    
    Base.metadata.create_all(bind=engine)

# Função auxiliar para obter uma sessão de banco de dados
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