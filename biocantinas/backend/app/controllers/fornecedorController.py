from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..dtos.fornecedorDTO import Fornecedor, FornecedorCreate, FornecedorUpdateAprovacao, OrdemFornecedor, ProdutoFornecedorAdd
from ..services.fornecedorService import get_services
from ..auth.jwt import get_current_user, require_role
from ..dtos.userDTO import User
from ..models.catalogo_produtos import produto_existe, CATALOGO_PRODUTOS

router = APIRouter(tags=["fornecedores"])

@router.get("/fornecedores", response_model=List[Fornecedor])
def listar_fornecedores():
    svc = get_services()
    return svc.listar_fornecedores()

@router.get("/fornecedores/ordem", response_model=List[OrdemFornecedor])
def obter_ordem_por_produto():
    svc = get_services()
    return svc.calcular_ordem_por_produto()

@router.get("/fornecedores/meu-perfil", response_model=Fornecedor)
def obter_meu_perfil(user: User = Depends(get_current_user)):
    """Retorna o perfil de fornecedor do usuário logado"""
    svc = get_services()
    fornecedor = svc.obter_fornecedor_por_usuario_id(user.id)
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Perfil de fornecedor não encontrado")
    return fornecedor

@router.post("/fornecedores/meu-perfil/produtos", response_model=Fornecedor)
def adicionar_produto_meu_perfil(produto: ProdutoFornecedorAdd, user: User = Depends(require_role("PRODUTOR"))):
    """Adiciona um novo produto ao perfil de fornecedor do usuário logado"""
    svc = get_services()
    
    # ✅ Validar que o produto existe no catálogo
    if not produto_existe(produto.nome):
        produtos_validos = sorted(CATALOGO_PRODUTOS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Produto '{produto.nome}' não existe no catálogo. "
                   f"Produtos válidos: {', '.join(produtos_validos[:10])}... "
                   f"(total de {len(produtos_validos)} produtos)"
        )
    
    try:
        return svc.adicionar_produto_fornecedor(user.id, produto)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/fornecedores", response_model=Fornecedor)
def criar_fornecedor(fornecedor: FornecedorCreate, user: User = Depends(require_role("PRODUTOR"))):
    svc = get_services()
    
    # ✅ Validar que produtos existem no catálogo
    for produto in fornecedor.produtos:
        if not produto_existe(produto.nome):
            produtos_validos = sorted(CATALOGO_PRODUTOS.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Produto '{produto.nome}' não existe no catálogo. "
                       f"Produtos válidos: {', '.join(produtos_validos[:10])}... "
                       f"(total de {len(produtos_validos)} produtos)"
            )
    
    return svc.criar_fornecedor(fornecedor, user.id)

@router.get("/fornecedores/{fid}", response_model=Fornecedor)
def obter_fornecedor(fid: int):
    svc = get_services()
    f = svc.obter_fornecedor(fid)
    if not f:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return f

@router.patch("/fornecedores/{fid}/aprovacao", response_model=Fornecedor)
def aprovar_fornecedor(fid: int, body: FornecedorUpdateAprovacao, user: User = Depends(require_role("GESTOR"))):
    svc = get_services()
    try:
        return svc.aprovar_fornecedor(fid, body.aprovado)
    except ValueError:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
