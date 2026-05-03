"""
Aplicação principal FastAPI - Catálogo de Produtos e Categorias.
Grupo 2 - Serviços de Redes para Internet.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routes import categorias_router, produtos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cria as tabelas no banco de dados ao iniciar a aplicação."""
    Base.metadata.create_all(bind=engine)
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
