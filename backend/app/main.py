"""
Aplicação principal FastAPI - Catálogo de Produtos e Categorias.
Grupo 2 - Serviços de Redes para Internet.
"""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routes import categorias_router, produtos_router
from .logger import log_startup, log_request, log_db_error


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cria as tabelas no banco de dados ao iniciar a aplicação."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        log_db_error(str(e))
        raise

    # Log de inicialização da aplicação (obrigatório pelo enunciado).
    log_startup()
    yield


app = FastAPI(
    title="Catálogo de Produtos e Categorias",
    description="API para gerenciamento de produtos e categorias - Grupo 2",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/api",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """
    Middleware que registra cada requisição recebida no Loki.
    Loga: método HTTP, rota e código de resposta.
    """
    response = await call_next(request)

    # Logar a requisição (obrigatório pelo enunciado).
    log_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
    )

    return response


# Registrar rotas
app.include_router(categorias_router)
app.include_router(produtos_router)


@app.get("/", tags=["Root"])
def root():
    """Rota raiz da API."""
    return {
        "mensagem": "API Catálogo de Produtos e Categorias",
        "versao": "1.0.0",
        "documentacao": "/api/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Verificação de saúde da aplicação."""
    return {"status": "ok"}
