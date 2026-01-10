from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db.session import get_db
from ..services.produtoCatalogoService import ProdutoCatalogoService
from ..dtos.produtoDTO import ProdutoCatalogoDTO, ProdutoCatalogoCreateDTO, ProdutoCatalogoUpdateDTO

router = APIRouter(prefix="/produtos-catalogo", tags=["Catálogo de Produtos"])


@router.get("/", response_model=List[ProdutoCatalogoDTO])
def listar_produtos(
    apenas_ativos: bool = True,
    db: Session = Depends(get_db)
):
    """Lista todos os produtos do catálogo global"""
    return ProdutoCatalogoService.listar_produtos(db, apenas_ativos)


@router.get("/{produto_id}", response_model=ProdutoCatalogoDTO)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Busca um produto específico por ID"""
    produto = ProdutoCatalogoService.buscar_produto(db, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail=f"Produto com ID {produto_id} não encontrado")
    return produto


@router.get("/nome/{nome}", response_model=ProdutoCatalogoDTO)
def buscar_por_nome(nome: str, db: Session = Depends(get_db)):
    """Busca um produto por nome exato"""
    produto = ProdutoCatalogoService.buscar_por_nome(db, nome)
    if not produto:
        raise HTTPException(status_code=404, detail=f"Produto '{nome}' não encontrado")
    return produto


@router.get("/pesquisar/{termo}", response_model=List[ProdutoCatalogoDTO])
def pesquisar_produtos(termo: str, db: Session = Depends(get_db)):
    """Pesquisa produtos por nome parcial"""
    return ProdutoCatalogoService.pesquisar_produtos(db, termo)


@router.get("/tipo/{tipo}", response_model=List[ProdutoCatalogoDTO])
def listar_por_tipo(tipo: str, db: Session = Depends(get_db)):
    """Lista produtos de um tipo específico (fruta, hortícola, proteína, etc.)"""
    return ProdutoCatalogoService.listar_por_tipo(db, tipo)


@router.get("/epoca/{epoca}", response_model=List[ProdutoCatalogoDTO])
def listar_por_epoca(epoca: str, db: Session = Depends(get_db)):
    """Lista produtos de uma época específica (Outono, Inverno, Primavera, Verão)"""
    return ProdutoCatalogoService.listar_por_epoca(db, epoca)


@router.post("/", response_model=ProdutoCatalogoDTO, status_code=201)
def criar_produto(produto: ProdutoCatalogoCreateDTO, db: Session = Depends(get_db)):
    """Cria um novo produto no catálogo global"""
    try:
        return ProdutoCatalogoService.criar_produto(db, produto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{produto_id}", response_model=ProdutoCatalogoDTO)
def atualizar_produto(
    produto_id: int,
    produto: ProdutoCatalogoUpdateDTO,
    db: Session = Depends(get_db)
):
    """Atualiza um produto do catálogo"""
    try:
        produto_atualizado = ProdutoCatalogoService.atualizar_produto(db, produto_id, produto)
        if not produto_atualizado:
            raise HTTPException(status_code=404, detail=f"Produto com ID {produto_id} não encontrado")
        return produto_atualizado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{produto_id}/desativar", status_code=204)
def desativar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Desativa um produto (soft delete)"""
    sucesso = ProdutoCatalogoService.desativar_produto(db, produto_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail=f"Produto com ID {produto_id} não encontrado")


@router.delete("/{produto_id}", status_code=204)
def remover_produto(produto_id: int, db: Session = Depends(get_db)):
    """Remove permanentemente um produto do catálogo (apenas se não houver fornecedores associados)"""
    try:
        sucesso = ProdutoCatalogoService.remover_produto(db, produto_id)
        if not sucesso:
            raise HTTPException(status_code=404, detail=f"Produto com ID {produto_id} não encontrado")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
