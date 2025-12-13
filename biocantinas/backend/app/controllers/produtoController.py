from fastapi import APIRouter, HTTPException, Depends
from ..dtos.produtoDTO import ProdutoDTO, ProdutoCreateDTO, ProdutoUpdateDTO
from ..services.produtoService import get_produto_service
from ..auth.jwt import get_current_user, require_role
from ..dtos.userDTO import User

router = APIRouter(tags=["produtos"], prefix="/produtos")


@router.post("/fornecedor/{fornecedor_id}", response_model=ProdutoDTO)
def criar_produto(
    fornecedor_id: int,
    produto: ProdutoCreateDTO,
    user: User = Depends(require_role("PRODUTOR"))
):
    """Adiciona um produto a um fornecedor existente"""
    svc = get_produto_service()
    try:
        return svc.criar_produto(fornecedor_id, produto)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{produto_id}", response_model=ProdutoDTO)
def obter_produto(produto_id: int, user: User = Depends(get_current_user)):
    """Obtém detalhes de um produto específico"""
    svc = get_produto_service()
    produto = svc.obter_produto(produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.put("/{produto_id}", response_model=ProdutoDTO)
def atualizar_produto(
    produto_id: int,
    produto: ProdutoUpdateDTO,
    user: User = Depends(require_role("PRODUTOR"))
):
    """Atualiza informações de um produto"""
    svc = get_produto_service()
    atualizado = svc.atualizar_produto(produto_id, produto)
    if not atualizado:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return atualizado


@router.delete("/{produto_id}")
def deletar_produto(
    produto_id: int,
    user: User = Depends(require_role("PRODUTOR"))
):
    """Remove um produto"""
    svc = get_produto_service()
    sucesso = svc.deletar_produto(produto_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"message": "Produto removido com sucesso"}
