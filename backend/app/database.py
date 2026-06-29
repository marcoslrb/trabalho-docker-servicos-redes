"""
Configuração de conexão com o banco de dados PostgreSQL.
Utiliza variáveis de ambiente para configurar a conexão.
Suporte a leitura de senha via arquivo montado (Secret do Kubernetes).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


def _read_secret(env_var: str, default: str, secret_file: str | None = None) -> str:
    """
    Lê um valor de configuração. Prioridade:
    1. Arquivo montado (secret_file), se existir
    2. Variável de ambiente (env_var)
    3. Valor padrão (default)
    """
    if secret_file and os.path.isfile(secret_file):
        with open(secret_file, "r") as f:
            return f.read().strip()
    return os.environ.get(env_var, default)


# Leitura das variáveis de ambiente para conexão com o banco
POSTGRES_USER = _read_secret("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = _read_secret("POSTGRES_PASSWORD", "20231001")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB = _read_secret("POSTGRES_DB", "catalogo_db")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency que fornece uma sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        # Logar erro de conexão com o banco ao Loki.
        from .logger import log_db_error
        log_db_error(str(e))
        raise
    finally:
        db.close()

