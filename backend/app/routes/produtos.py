"""
Rotas CRUD para a entidade Produto.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from ..database import get_db
from ..models import Produto, Categoria
from ..schemas import ProdutoCreate, ProdutoUpdate, ProdutoResponse

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("/", response_model=List[ProdutoResponse])
def listar_produtos(
    categoria_id: int | None = None,
    db: Session = Depends(get_db)
):
    """Lista todos os produtos, com filtro opcional por categoria."""
    query = db.query(Produto).options(joinedload(Produto.categoria))

    if categoria_id is not None:
        query = query.filter(Produto.categoria_id == categoria_id)

    return query.all()


@router.get("/{produto_id}", response_model=ProdutoResponse)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    """Obtém um produto pelo ID."""
    produto = (
        db.query(Produto)
        .options(joinedload(Produto.categoria))
        .filter(Produto.id == produto_id)
        .first()
    )
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com id {produto_id} não encontrado"
        )
    return produto


@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    """Cria um novo produto."""
    # Verificar se a categoria existe
    categoria = db.query(Categoria).filter(Categoria.id == produto.categoria_id).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categoria com id {produto.categoria_id} não encontrada"
        )

    db_produto = Produto(**produto.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)

    # Recarregar com o relacionamento
    db_produto = (
        db.query(Produto)
        .options(joinedload(Produto.categoria))
        .filter(Produto.id == db_produto.id)
        .first()
    )
    return db_produto


@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    produto: ProdutoUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um produto existente."""
    db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not db_produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com id {produto_id} não encontrado"
        )

    dados = produto.model_dump(exclude_unset=True)

    # Se estiver atualizando a categoria, verificar se ela existe
    if "categoria_id" in dados:
        categoria = db.query(Categoria).filter(Categoria.id == dados["categoria_id"]).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Categoria com id {dados['categoria_id']} não encontrada"
            )

    for campo, valor in dados.items():
        setattr(db_produto, campo, valor)

    db.commit()
    db.refresh(db_produto)

    # Recarregar com o relacionamento
    db_produto = (
        db.query(Produto)
        .options(joinedload(Produto.categoria))
        .filter(Produto.id == db_produto.id)
        .first()
    )
    return db_produto


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Remove um produto pelo ID."""
    db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not db_produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com id {produto_id} não encontrado"
        )

    db.delete(db_produto)
    db.commit()
    return None
