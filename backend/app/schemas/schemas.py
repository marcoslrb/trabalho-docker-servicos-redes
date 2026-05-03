"""
Schemas Pydantic para validação de dados das entidades Categoria e Produto.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ========================
# Schemas de Categoria
# ========================

class CategoriaBase(BaseModel):
    """Schema base para Categoria."""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome da categoria")
    descricao: Optional[str] = Field(None, description="Descrição da categoria")


class CategoriaCreate(CategoriaBase):
    """Schema para criação de uma nova categoria."""
    pass


class CategoriaUpdate(BaseModel):
    """Schema para atualização de uma categoria."""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = None


class CategoriaResponse(CategoriaBase):
    """Schema de resposta para Categoria."""
    id: int
    criado_em: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ========================
# Schemas de Produto
# ========================

class ProdutoBase(BaseModel):
    """Schema base para Produto."""
    nome: str = Field(..., min_length=1, max_length=200, description="Nome do produto")
    descricao: Optional[str] = Field(None, description="Descrição do produto")
    preco: float = Field(..., gt=0, description="Preço do produto")
    estoque: int = Field(0, ge=0, description="Quantidade em estoque")
    categoria_id: int = Field(..., description="ID da categoria do produto")


class ProdutoCreate(ProdutoBase):
    """Schema para criação de um novo produto."""
    pass


class ProdutoUpdate(BaseModel):
    """Schema para atualização de um produto."""
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = None
    preco: Optional[float] = Field(None, gt=0)
    estoque: Optional[int] = Field(None, ge=0)
    categoria_id: Optional[int] = None


class ProdutoResponse(ProdutoBase):
    """Schema de resposta para Produto."""
    id: int
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
    categoria: Optional[CategoriaResponse] = None

    model_config = {"from_attributes": True}
