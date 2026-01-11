"""
Script para RECRIAR completamente o banco de dados
Remove e cria tudo do zero com dados completos
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from datetime import date, timedelta, datetime
from biocantinas.backend.app.db.session import SessionLocal, engine, init_db
from biocantinas.backend.app.db.models import (
    Base, UserORM, FornecedorORM, FornecedorEstadoORM, ProdutoORM, ProdutoFornecedorORM, 
    EmentaORM, RefeicaoORM, ItemRefeicaoORM, ReservaRefeicaoORM,
    HistoricoRefeicoesDiaORM, HistoricoReservasPratoORM, ExecucaoRefeicaoORM,
    ReceitaORM, ItemReceitaORM
)
from biocantinas.backend.app.models.catalogo_produtos import CATALOGO_PRODUTOS
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def obter_tipo_produto(nome_produto):
    """Obtém o tipo de um produto do catálogo"""
    if nome_produto in CATALOGO_PRODUTOS:
        return CATALOGO_PRODUTOS[nome_produto].categoria
    return None

def delete_database(db_url: str):
    """Remove arquivos de banco de dados """
    base_dir = Path(__file__).parent.parent
    targets = set()

    backend_db = base_dir / "biocantinas" / "backend" / "biocantinas.db"
    targets.add(backend_db)

    if db_url.startswith("sqlite:///"):
        db_path_str = db_url.replace("sqlite:///", "", 1)
        db_path = Path(db_path_str)
        if not db_path.is_absolute():
            db_path = (base_dir / db_path_str).resolve()
        targets.add(db_path)

    for path in targets:
        if path.exists():
            print(f"Removing existing database: {path}")
            path.unlink()
            print("Database removed")
        else:
            print(f"No database found at {path}")


def create_users(session):
    """Criar usuários do sistema"""
    print("\n👤 Criando usuários...")
    
    users = [
        UserORM(username="gestor", hashed_password=pwd_context.hash("1"), role="GESTOR_CANTINA", is_active=True),
        UserORM(username="dietista", hashed_password=pwd_context.hash("1"), role="DIETISTA", is_active=True),
        UserORM(username="aluno1", hashed_password=pwd_context.hash("1"), role="ALUNO", is_active=True),
        UserORM(username="aluno2", hashed_password=pwd_context.hash("1"), role="ALUNO", is_active=True),
        UserORM(username="joao", hashed_password=pwd_context.hash("1"), role="PRODUTOR", is_active=True),
        UserORM(username="maria", hashed_password=pwd_context.hash("1"), role="PRODUTOR", is_active=True),
        UserORM(username="pedro", hashed_password=pwd_context.hash("1"), role="PRODUTOR", is_active=True),
        UserORM(username="ana", hashed_password=pwd_context.hash("1"), role="PRODUTOR", is_active=True),
        UserORM(username="carlos", hashed_password=pwd_context.hash("1"), role="PRODUTOR", is_active=True),
        UserORM(username="lucas", hashed_password=pwd_context.hash("1"), role="PRODUTOR", is_active=True),
        UserORM(username="rita", hashed_password=pwd_context.hash("1"), role="PRODUTOR", is_active=True),
        UserORM(username="miguel", hashed_password=pwd_context.hash("1"), role="PRODUTOR", is_active=True),
        UserORM(username="sofia", hashed_password=pwd_context.hash("1"), role="PRODUTOR", is_active=True),
        UserORM(username="bruno", hashed_password=pwd_context.hash("1"), role="PRODUTOR", is_active=True),
        UserORM(username="carla", hashed_password=pwd_context.hash("1"), role="PRODUTOR", is_active=True),
    ]
    
    for user in users:
        session.add(user)
    session.commit()
    print(f"✅ {len(users)} usuários criados")
    
    # Return users for linking with suppliers
    return {user.username: user.id for user in users}


def create_fornecedores(session, user_ids):
    """Criar fornecedores e seus produtos com unidades coerentes"""
    print("\n🚜 Criando fornecedores...")
    today = date.today()
    
    # Fornecedores vinculados aos usuários produtores via usuario_id
    # Considerando: unidades apropriadas, semanas de produção e capacidade semanal
    fornecedores_data = [
        # João - Frutas variadas (kg)
        {
            "nome": "João Silva - Pomares Bio",
            "usuario_id": user_ids["joao"],
            "data_inscricao": today - timedelta(days=60),
            "aprovado": True,
            "local": True,
            "certificado": True,
            "freguesia": "Freigil e Miomães",
            "produtos": [
                {"nome": "Maçã", "semana_inicio": 35, "semana_fim": 52, "capacidade": 150, "unidade": "kg", "biologico": True},
                {"nome": "Pera", "semana_inicio": 32, "semana_fim": 48, "capacidade": 80, "unidade": "kg", "biologico": True},
                {"nome": "Laranja", "semana_inicio": 40, "semana_fim": 52, "capacidade": 120, "unidade": "kg", "biologico": True},
                {"nome": "Morango", "semana_inicio": 16, "semana_fim": 26, "capacidade": 60, "unidade": "kg", "biologico": True},
            ]
        },
        # Maria - Hortícolas (kg)
        {
            "nome": "Maria Carvalho - Horta Ecológica",
            "usuario_id": user_ids["maria"],
            "data_inscricao": today - timedelta(days=75),
            "aprovado": True,
            "local": True,
            "certificado": True,
            "freguesia": "Cinfães",
            "produtos": [
                {"nome": "Tomate", "semana_inicio": 20, "semana_fim": 43, "capacidade": 180, "unidade": "kg", "biologico": True},
                {"nome": "Alface", "semana_inicio": 15, "semana_fim": 50, "capacidade": 100, "unidade": "kg", "biologico": True},
                {"nome": "Cenoura", "semana_inicio": 11, "semana_fim": 9, "capacidade": 140, "unidade": "kg", "biologico": True},
                {"nome": "Couve", "semana_inicio": 15, "semana_fim": 50, "capacidade": 90, "unidade": "kg", "biologico": True},
                {"nome": "Beterraba", "semana_inicio": 25, "semana_fim": 48, "capacidade": 110, "unidade": "kg", "biologico": True},
            ]
        },
        # Pedro - Carnes e Ovos (kg)
        {
            "nome": "Pedro Santos - Quinta Bio",
            "usuario_id": user_ids["pedro"],
            "data_inscricao": today - timedelta(days=45),
            "aprovado": True,
            "local": True,
            "certificado": True,
            "freguesia": "Souselo",
            "produtos": [
                {"nome": "Frango", "semana_inicio": 11, "semana_fim": 9, "capacidade": 200, "unidade": "kg", "biologico": True},
                {"nome": "Ovos", "semana_inicio": 11, "semana_fim": 9, "capacidade": 300, "unidade": "unidades", "biologico": True},
            ]
        },
        # Ana - Laticínios (L, kg)
        {
            "nome": "Ana Costa - Queijaria do Vale",
            "usuario_id": user_ids["ana"],
            "data_inscricao": today - timedelta(days=90),
            "aprovado": True,
            "local": False,
            "certificado": True,
            "freguesia": "Travanca",
            "produtos": [
                {"nome": "Leite", "semana_inicio": 11, "semana_fim": 9, "capacidade": 300, "unidade": "L", "biologico": True},
                {"nome": "Queijo", "semana_inicio": 11, "semana_fim": 9, "capacidade": 40, "unidade": "kg", "biologico": True},
                {"nome": "Iogurte", "semana_inicio": 1, "semana_fim": 52, "capacidade": 150, "unidade": "L", "biologico": True},
            ]
        },
        # Carlos - Proteínas alternativas (kg)
        {
            "nome": "Carlos Ribeiro - Carnes Bio",
            "usuario_id": user_ids["carlos"],
            "data_inscricao": today - timedelta(days=55),
            "aprovado": True,
            "local": False,
            "certificado": False,
            "freguesia": "Bustelo",
            "produtos": [
                {"nome": "Carne de Vaca", "semana_inicio": 11, "semana_fim": 9, "capacidade": 120, "unidade": "kg", "biologico": True},
                {"nome": "Peru", "semana_inicio": 11, "semana_fim": 9, "capacidade": 90, "unidade": "kg", "biologico": True},
            ]
        },
        # Lucas - Frango (segunda opção, menor prioridade)
        {
            "nome": "Lucas Ferreira - Aves Premium",
            "usuario_id": user_ids["lucas"],
            "data_inscricao": today - timedelta(days=20),
            "aprovado": True,
            "local": True,
            "certificado": False,
            "freguesia": "Tarouquela",
            "produtos": [
                {"nome": "Frango", "semana_inicio": 11, "semana_fim": 9, "capacidade": 150, "unidade": "kg", "biologico": True},
            ]
        },
        # Rita - Hortícolas especiais (kg)
        {
            "nome": "Rita Gomes - Horta da Montanha",
            "usuario_id": user_ids["rita"],
            "data_inscricao": today - timedelta(days=65),
            "aprovado": True,
            "local": True,
            "certificado": True,
            "freguesia": "Moimenta",
            "produtos": [
                {"nome": "Espinafre", "semana_inicio": 20, "semana_fim": 45, "capacidade": 70, "unidade": "kg", "biologico": True},
                {"nome": "Pimento", "semana_inicio": 22, "semana_fim": 42, "capacidade": 85, "unidade": "kg", "biologico": True},
                {"nome": "Abóbora", "semana_inicio": 28, "semana_fim": 50, "capacidade": 100, "unidade": "kg", "biologico": True},
            ]
        },
        # Miguel - Peixes (kg)
        {
            "nome": "Miguel Silva - Peixaria Fresca",
            "usuario_id": user_ids["miguel"],
            "data_inscricao": today - timedelta(days=50),
            "aprovado": True,
            "local": False,
            "certificado": False,
            "freguesia": "Oliveira do Douro",
            "produtos": [
                {"nome": "Peixe", "semana_inicio": 11, "semana_fim": 9, "capacidade": 100, "unidade": "kg", "biologico": False},
                {"nome": "Bacalhau", "semana_inicio": 11, "semana_fim": 9, "capacidade": 70, "unidade": "kg", "biologico": False},
            ]
        },
        # Sofia - Hortícolas diversas (kg)
        {
            "nome": "Sofia Costa - Quinta do Sertão",
            "usuario_id": user_ids["sofia"],
            "data_inscricao": today - timedelta(days=70),
            "aprovado": True,
            "local": True,
            "certificado": True,
            "freguesia": "Nespereira",
            "produtos": [
                {"nome": "Batata", "semana_inicio": 28, "semana_fim": 48, "capacidade": 200, "unidade": "kg", "biologico": True},
                {"nome": "Cebola", "semana_inicio": 32, "semana_fim": 52, "capacidade": 120, "unidade": "kg", "biologico": True},
                {"nome": "Alho", "semana_inicio": 32, "semana_fim": 52, "capacidade": 30, "unidade": "kg", "biologico": True},
            ]
        },
        # Bruno - Batata (segundo fornecedor, menor prioridade)
        {
            "nome": "Bruno Ferreira - Raízes Bio",
            "usuario_id": user_ids["bruno"],
            "data_inscricao": today - timedelta(days=15),
            "aprovado": True,
            "local": False,
            "certificado": True,
            "freguesia": "Ferreiros de Tendais",
            "produtos": [
                {"nome": "Batata", "semana_inicio": 28, "semana_fim": 48, "capacidade": 180, "unidade": "kg", "biologico": True},
            ]
        },
        # Carla - Hortícolas (kg)
        {
            "nome": "Carla Mendes - Horta do Vale",
            "usuario_id": user_ids["carla"],
            "data_inscricao": today - timedelta(days=40),
            "aprovado": True,
            "local": True,
            "certificado": True,
            "freguesia": "Alhões",
            "produtos": [
                {"nome": "Tomate", "semana_inicio": 20, "semana_fim": 43, "capacidade": 150, "unidade": "kg", "biologico": True},
                {"nome": "Alface", "semana_inicio": 15, "semana_fim": 50, "capacidade": 80, "unidade": "kg", "biologico": True},
                {"nome": "Cenoura", "semana_inicio": 1, "semana_fim": 52, "capacidade": 120, "unidade": "kg", "biologico": True},
            ]
        },
    ]
    
    produto_index = 0
    for data in fornecedores_data:
        fornecedor = FornecedorORM(
            nome=data["nome"],
            usuario_id=data["usuario_id"],
            data_inscricao=data["data_inscricao"],
            aprovado=data["aprovado"],
            local=data.get("local", False),
            certificado=data.get("certificado", False),
        )
        session.add(fornecedor)
        session.flush()
        # Estado sanitário / localização
        estado = FornecedorEstadoORM(
            fornecedor_id=fornecedor.id,
            em_quarentena=False,
            freguesia=data.get("freguesia")
        )
        session.add(estado)
        
        for p in data["produtos"]:
            # Buscar ou criar produto no catálogo
            produto_catalogo = session.query(ProdutoORM).filter_by(nome=p['nome']).first()
            if not produto_catalogo:
                produto_catalogo = ProdutoORM(
                    nome=p['nome'],
                    tipo=obter_tipo_produto(p['nome']),
                    unidade_medida=p['unidade'],
                    ativo=True
                )
                session.add(produto_catalogo)
                session.flush()
            
            produto_fornecedor = ProdutoFornecedorORM(
                fornecedor_id=fornecedor.id,
                produto_id=produto_catalogo.id,
                biologico=p['biologico'],
                semana_producao_inicio=p['semana_inicio'],
                semana_producao_fim=p['semana_fim'],
                capacidade=p['capacidade'],
                unidade_medida=p['unidade'],
                data_inscricao=p.get("data_inscricao") or (datetime.utcnow() - timedelta(days=produto_index))
            )
            session.add(produto_fornecedor)
            produto_index += 1
    
    session.commit()
    print(f"✅ {len(fornecedores_data)} fornecedores criados com produtos coerentes")

def create_receitas(session):
    """Criar receitas fixas do catálogo"""
    print("\n🍽️  Criando catálogo de receitas...")
    from biocantinas.backend.app.models.receitas_catalogo import RECEITAS_CATOLOG
    
    for receita_dados in RECEITAS_CATOLOG:
        # Verificar se a receita já existe
        receita_existente = session.query(ReceitaORM).filter_by(nome=receita_dados["nome"]).first()
        if receita_existente:
            print(f"  ⏭️  Receita '{receita_dados['nome']}' já existe")
            continue
        
        # Criar receita
        receita = ReceitaORM(
            nome=receita_dados["nome"],
            descricao=receita_dados.get("descricao"),
            tipo_refeicao=receita_dados.get("tipo_refeicao"),
            categoria=receita_dados.get("categoria"),
            porcoes_base=receita_dados.get("porcoes_base", 1),
            tempo_preparo=receita_dados.get("tempo_preparo"),
            ativa=True
        )
        session.add(receita)
        session.flush()  # Para obter o ID da receita
        
        # Adicionar ingredientes
        for ingrediente_dados in receita_dados.get("ingredientes", []):
            # Procurar o produto no catálogo
            produto = session.query(ProdutoORM).filter_by(
                nome=ingrediente_dados["produto"]
            ).first()
            
            if not produto:
                # Se o produto não existir, criar
                produto = ProdutoORM(
                    nome=ingrediente_dados["produto"],
                    tipo=obter_tipo_produto(ingrediente_dados["produto"]),
                    ativo=True,
                    unidade_medida="kg"
                )
                session.add(produto)
                session.flush()
            
            # Criar item da receita
            item_receita = ItemReceitaORM(
                receita_id=receita.id,
                produto_catalogo_id=produto.id,
                quantidade_por_porcao=ingrediente_dados["quantidade_por_porcao"]
            )
            session.add(item_receita)
        
        print(f"  ✅ Receita '{receita_dados['nome']}' criada com {len(receita_dados.get('ingredientes', []))} ingredientes")
    
    session.commit()
    print(f"✅ Catálogo de receitas criado")

def create_ementas(session):
    """Criar ementas com refeições completas"""
    print("\n📋 Criando ementas...")
    
    # Ementa Semana 1: 10-16 Dez (Terça a Segunda)
    ementa1 = EmentaORM(
        nome="Ementa Semana 10-16 Dez",
        data_inicio=date(2025, 12, 10),
        data_fim=date(2025, 12, 16)
    )
    session.add(ementa1)
    session.flush()
    
    # Refeições da semana (dia_semana: 1=Segunda, 2=Terça, 3=Quarta, 4=Quinta, 5=Sexta)
    refeicoes1 = [
        # SEGUNDA-FEIRA (dia_semana=1) - 15 Dez
        # Opção 1 - Almoço
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=1,
            tipo="almoço",
            descricao="Frango grelhado com batata e legumes",
            itens=[
                ItemRefeicaoORM(ingrediente="frango", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
            ]
        ),
        # Opção 2 - Almoço
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=1,
            tipo="almoço",
            descricao="Peixe com arroz e salada",
            itens=[
                ItemRefeicaoORM(ingrediente="pescada", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="arroz", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=0.1),
            ]
        ),
        # Opção 1 - Jantar
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=1,
            tipo="jantar",
            descricao="Sopa de legumes e sanduíche",
            itens=[
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="couve", quantidade_estimada=0.1),
            ]
        ),
        # Opção 2 - Jantar
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=1,
            tipo="jantar",
            descricao="Omelete com salada",
            itens=[
                ItemRefeicaoORM(ingrediente="Ovos", quantidade_estimada=3),
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=0.1),
            ]
        ),
        # TERÇA-FEIRA (dia_semana=2) - 10 Dez
        # Opção 1 - Almoço
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=2,
            tipo="almoço",
            descricao="Peixe assado com arroz",
            itens=[
                ItemRefeicaoORM(ingrediente="pescada", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="beterraba", quantidade_estimada=0.12),
            ]
        ),
        # Opção 2 - Almoço
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=2,
            tipo="almoço",
            descricao="Carne de vaca com batata",
            itens=[
                ItemRefeicaoORM(ingrediente="carne de vaca", quantidade_estimada=0.12),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
            ]
        ),
        # Opção 1 - Jantar
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=2,
            tipo="jantar",
            descricao="Salada completa com frango",
            itens=[
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="frango", quantidade_estimada=0.15),
            ]
        ),
        # Opção 2 - Jantar
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=2,
            tipo="jantar",
            descricao="Sopa de peixe",
            itens=[
                ItemRefeicaoORM(ingrediente="pescada", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
            ]
        ),
        # QUARTA-FEIRA (dia_semana=3) - 11 Dez
        # Opção 1 - Almoço
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=3,
            tipo="almoço",
            descricao="Lasanha vegetariana",
            itens=[
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="queijo", quantidade_estimada=0.08),
                ItemRefeicaoORM(ingrediente="espinafre", quantidade_estimada=0.08),
                ItemRefeicaoORM(ingrediente="curgete", quantidade_estimada=0.1),
            ]
        ),
        # Opção 2 - Almoço
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=3,
            tipo="almoço",
            descricao="Salmão grelhado com legumes",
            itens=[
                ItemRefeicaoORM(ingrediente="salmão", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="beterraba", quantidade_estimada=0.12),
                ItemRefeicaoORM(ingrediente="couve", quantidade_estimada=0.1),
            ]
        ),
        # Opção 1 - Jantar
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=3,
            tipo="jantar",
            descricao="Creme de abóbora com pão",
            itens=[
                ItemRefeicaoORM(ingrediente="batata doce", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
            ]
        ),
        # Opção 2 - Jantar
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=3,
            tipo="jantar",
            descricao="Massa com molho de tomate",
            itens=[
                ItemRefeicaoORM(ingrediente="massa", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="queijo", quantidade_estimada=0.08),
            ]
        ),
        # QUINTA-FEIRA (dia_semana=4) - 12 Dez
        # Opção 1 - Almoço
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=4,
            tipo="almoço",
            descricao="Carne de vaca estufada com batatas",
            itens=[
                ItemRefeicaoORM(ingrediente="carne de vaca", quantidade_estimada=0.12),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
            ]
        ),
        # Opção 2 - Almoço
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=4,
            tipo="almoço",
            descricao="Peru assado com batata doce",
            itens=[
                ItemRefeicaoORM(ingrediente="peru", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="batata doce", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="couve", quantidade_estimada=0.1),
            ]
        ),
        # Opção 1 - Jantar
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=4,
            tipo="jantar",
            descricao="Pizza vegetariana",
            itens=[
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="queijo", quantidade_estimada=0.08),
                ItemRefeicaoORM(ingrediente="pimento", quantidade_estimada=1),
            ]
        ),
        # Opção 2 - Jantar
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=4,
            tipo="jantar",
            descricao="Bacalhau com natas",
            itens=[
                ItemRefeicaoORM(ingrediente="bacalhau", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="queijo", quantidade_estimada=0.08),
            ]
        ),
        # SEXTA-FEIRA (dia_semana=5) - 13 Dez
        # Opção 1 - Almoço
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=5,
            tipo="almoço",
            descricao="Salmão grelhado com legumes",
            itens=[
                ItemRefeicaoORM(ingrediente="salmão", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="beterraba", quantidade_estimada=0.12),
                ItemRefeicaoORM(ingrediente="couve", quantidade_estimada=0.1),
            ]
        ),
        # Opção 2 - Almoço
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=5,
            tipo="almoço",
            descricao="Arroz de frango",
            itens=[
                ItemRefeicaoORM(ingrediente="frango", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="arroz", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
            ]
        ),
        # Opção 1 - Jantar
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=5,
            tipo="jantar",
            descricao="Wrap de frango com salada",
            itens=[
                ItemRefeicaoORM(ingrediente="frango", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=0.1),
            ]
        ),
        # Opção 2 - Jantar
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=5,
            tipo="jantar",
            descricao="Salada de atum",
            itens=[
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="Ovos", quantidade_estimada=3),
            ]
        ),
    ]
    
    for refeicao in refeicoes1:
        session.add(refeicao)
    
    # Ementa Semana 2: 17-23 Dez
    ementa2 = EmentaORM(
        nome="Ementa Semana 17-23 Dez",
        data_inicio=date(2025, 12, 17),
        data_fim=date(2025, 12, 23)
    )
    session.add(ementa2)
    session.flush()
    
    refeicoes2 = [
        # SEGUNDA-FEIRA (dia_semana=1) - 22 Dez
        RefeicaoORM(
            ementa_id=ementa2.id,
            dia_semana=1,
            tipo="almoço",
            descricao="Peru assado com batata doce",
            itens=[
                ItemRefeicaoORM(ingrediente="peru", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="batata doce", quantidade_estimada=0.15),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa2.id,
            dia_semana=1,
            tipo="jantar",
            descricao="Sopa de peixe",
            itens=[
                ItemRefeicaoORM(ingrediente="pescada", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
            ]
        ),
        # TERÇA-FEIRA (dia_semana=2) - 17 Dez
        RefeicaoORM(
            ementa_id=ementa2.id,
            dia_semana=2,
            tipo="almoço",
            descricao="Bacalhau com natas",
            itens=[
                ItemRefeicaoORM(ingrediente="bacalhau", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="queijo", quantidade_estimada=0.08),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa2.id,
            dia_semana=2,
            tipo="jantar",
            descricao="Salada de atum",
            itens=[
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=0.1),
            ]
        ),
    ]
    
    for refeicao in refeicoes2:
        session.add(refeicao)
    
    # ============ EMENTAS PARA JANEIRO ============
    # Ementa Semana 1: 6-12 Jan (Inverno - Produtos de Época)
    ementa3 = EmentaORM(
        nome="Ementa Semana 6-12 Jan - Inverno Bio",
        data_inicio=date(2026, 1, 6),
        data_fim=date(2026, 1, 12)
    )
    session.add(ementa3)
    session.flush()
    
    refeicoes3 = [
        # SEGUNDA-FEIRA (dia_semana=1) - 6 Jan
        RefeicaoORM(
            ementa_id=ementa3.id,
            dia_semana=1,
            tipo="almoço",
            descricao="Carne de Vaca com Maçã e Batata",
            itens=[
                ItemRefeicaoORM(ingrediente="carne de vaca", quantidade_estimada=0.12),
                ItemRefeicaoORM(ingrediente="maçã", quantidade_estimada=0.18),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa3.id,
            dia_semana=1,
            tipo="almoço",
            descricao="Bacalhau com Couve à Brás",
            itens=[
                ItemRefeicaoORM(ingrediente="bacalhau", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="couve", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="cebola", quantidade_estimada=0.05),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa3.id,
            dia_semana=1,
            tipo="jantar",
            descricao="Sopa de Espinafre com Batata",
            itens=[
                ItemRefeicaoORM(ingrediente="espinafre", quantidade_estimada=0.08),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="cebola", quantidade_estimada=0.05),
                ItemRefeicaoORM(ingrediente="alho", quantidade_estimada=0.01),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa3.id,
            dia_semana=1,
            tipo="jantar",
            descricao="Omeleta com Alface e Laranja",
            itens=[
                ItemRefeicaoORM(ingrediente="Ovos", quantidade_estimada=3),
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="laranja", quantidade_estimada=0.15),
            ]
        ),
        # TERÇA-FEIRA (dia_semana=2) - 7 Jan
        RefeicaoORM(
            ementa_id=ementa3.id,
            dia_semana=2,
            tipo="almoço",
            descricao="Frango ao Molho de Pera",
            itens=[
                ItemRefeicaoORM(ingrediente="frango", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="pera", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa3.id,
            dia_semana=2,
            tipo="almoço",
            descricao="Peixe Branco com Beterraba",
            itens=[
                ItemRefeicaoORM(ingrediente="peixe", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="beterraba", quantidade_estimada=0.12),
                ItemRefeicaoORM(ingrediente="couve", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa3.id,
            dia_semana=2,
            tipo="jantar",
            descricao="Caldo Verde Invernal",
            itens=[
                ItemRefeicaoORM(ingrediente="couve", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="cebola", quantidade_estimada=0.05),
                ItemRefeicaoORM(ingrediente="alho", quantidade_estimada=0.01),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa3.id,
            dia_semana=2,
            tipo="jantar",
            descricao="Salada Morna de Beterraba",
            itens=[
                ItemRefeicaoORM(ingrediente="beterraba", quantidade_estimada=0.12),
                ItemRefeicaoORM(ingrediente="queijo", quantidade_estimada=0.08),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
            ]
        ),
        # QUARTA-FEIRA (dia_semana=3) - 8 Jan
        RefeicaoORM(
            ementa_id=ementa3.id,
            dia_semana=3,
            tipo="almoço",
            descricao="Ensopado de Peru com Legumes",
            itens=[
                ItemRefeicaoORM(ingrediente="peru", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="couve", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="alho", quantidade_estimada=0.01),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa3.id,
            dia_semana=3,
            tipo="almoço",
            descricao="Quiche de Espinafre e Queijo",
            itens=[
                ItemRefeicaoORM(ingrediente="espinafre", quantidade_estimada=0.08),
                ItemRefeicaoORM(ingrediente="queijo", quantidade_estimada=0.08),
                ItemRefeicaoORM(ingrediente="Ovos", quantidade_estimada=3),
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=0.1),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa3.id,
            dia_semana=3,
            tipo="jantar",
            descricao="Iogurte com Pera e Laranja",
            itens=[
                ItemRefeicaoORM(ingrediente="iogurte", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="pera", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="laranja", quantidade_estimada=0.15),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa3.id,
            dia_semana=3,
            tipo="jantar",
            descricao="Frango Grelhado com Cenoura",
            itens=[
                ItemRefeicaoORM(ingrediente="frango", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
            ]
        ),
    ]
    
    for refeicao in refeicoes3:
        session.add(refeicao)
    
    # Ementa Semana 2: 13-19 Jan
    ementa4 = EmentaORM(
        nome="Ementa Semana 13-19 Jan - Fevereiro Bio",
        data_inicio=date(2026, 1, 13),
        data_fim=date(2026, 1, 19)
    )
    session.add(ementa4)
    session.flush()
    
    refeicoes4 = [
        # SEGUNDA-FEIRA (dia_semana=1) - 13 Jan
        RefeicaoORM(
            ementa_id=ementa4.id,
            dia_semana=1,
            tipo="almoço",
            descricao="Bacalhau à Brás com Abóbora",
            itens=[
                ItemRefeicaoORM(ingrediente="bacalhau", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="cebola", quantidade_estimada=0.05),
                ItemRefeicaoORM(ingrediente="alho", quantidade_estimada=0.01),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa4.id,
            dia_semana=1,
            tipo="almoço",
            descricao="Carne Assada com Maçã Caramelizada",
            itens=[
                ItemRefeicaoORM(ingrediente="carne de vaca", quantidade_estimada=0.12),
                ItemRefeicaoORM(ingrediente="maçã", quantidade_estimada=0.18),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa4.id,
            dia_semana=1,
            tipo="jantar",
            descricao="Sopa de Abóbora com Leite",
            itens=[
                ItemRefeicaoORM(ingrediente="abóbora", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="leite", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="cebola", quantidade_estimada=0.05),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa4.id,
            dia_semana=1,
            tipo="jantar",
            descricao="Salada de Pera e Alface",
            itens=[
                ItemRefeicaoORM(ingrediente="pera", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="queijo", quantidade_estimada=0.08),
            ]
        ),
        # TERÇA-FEIRA (dia_semana=2) - 14 Jan
        RefeicaoORM(
            ementa_id=ementa4.id,
            dia_semana=2,
            tipo="almoço",
            descricao="Peixe com Laranja e Beterraba",
            itens=[
                ItemRefeicaoORM(ingrediente="peixe", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="laranja", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="beterraba", quantidade_estimada=0.12),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=0.1),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa4.id,
            dia_semana=2,
            tipo="almoço",
            descricao="Frango ao Leite com Abóbora",
            itens=[
                ItemRefeicaoORM(ingrediente="frango", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="leite", quantidade_estimada=0.1),
                ItemRefeicaoORM(ingrediente="abóbora", quantidade_estimada=0.2),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=0.2),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa4.id,
            dia_semana=2,
            tipo="jantar",
            descricao="Queijo com Beterraba Assada",
            itens=[
                ItemRefeicaoORM(ingrediente="queijo", quantidade_estimada=0.08),
                ItemRefeicaoORM(ingrediente="beterraba", quantidade_estimada=0.12),
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=0.1),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa4.id,
            dia_semana=2,
            tipo="jantar",
            descricao="Iogurte com Maçã",
            itens=[
                ItemRefeicaoORM(ingrediente="iogurte", quantidade_estimada=0.15),
                ItemRefeicaoORM(ingrediente="maçã", quantidade_estimada=0.18),
            ]
        ),
    ]
    
    for refeicao in refeicoes4:
        session.add(refeicao)
    
    session.commit()
    print(f"✅ 4 ementas criadas com {len(refeicoes1) + len(refeicoes2) + len(refeicoes3) + len(refeicoes4)} refeições")

def create_reservas(session):
    """Criar reservas de alunos para TODAS as refeições
    Baseado em ~300 alunos por dia"""
    print("\n📝 Criando reservas...")
    
    aluno1 = session.query(UserORM).filter_by(username="aluno1").first()
    aluno2 = session.query(UserORM).filter_by(username="aluno2").first()
    
    refeicoes = session.query(RefeicaoORM).all()
    
    if not aluno1 or not aluno2:
        print("⚠️  Alunos não encontrados")
        return
    
    if len(refeicoes) == 0:
        print("⚠️  Nenhuma refeição encontrada")
        return
    
    reservas = []
    
    # Criar reservas para TODAS as refeições
    # Quantidade varia baseado no histórico de 300 alunos
    # Distribuição: ~300 alunos distribuídos em 300 reservas por dia
    # Ajuste para ter 3 alertas >10% e alguns desvios 2-7%
    quantidades_por_tipo = {
        # Segunda - Almoço
        (1, "almoço", "Frango grelhado com batata e legumes"): 91,  # Histórico: 90 (+1.1%)
        (1, "almoço", "Peixe com arroz e salada"): 56,  # Histórico: 54 (+3.7%)
        (1, "almoço", "Sopa de legumes e sanduíche"): 42,  # Histórico: 36 ⚠️ (+16.7% ALERTA)
        (1, "almoço", "Omelete com salada"): 52,
        # Segunda - Jantar
        (1, "jantar", "Sopa de peixe"): 85,  # Histórico: 72 ⚠️ (+18.1% ALERTA)
        (1, "jantar", "Frango grelhado com legumes"): 30,
        (1, "jantar", "Salada mista"): 20,
        (1, "jantar", "Iogurte com fruta"): 10,
        
        # Terça - Almoço
        (2, "almoço", "Peixe assado com arroz"): 96,  # Histórico: 95 (+1.1%)
        (2, "almoço", "Carne de vaca com batata"): 57,  # Histórico: 57 (0%)
        (2, "almoço", "Salada completa com frango"): 38,
        (2, "almoço", "Sopa de peixe"): 40,
        # Terça - Jantar
        (2, "jantar", "Sopa de legumes e sanduíche"): 42,
        (2, "jantar", "Omelete com salada"): 45,  # Histórico: 44 (+2.3%)
        (2, "jantar", "Pão com margarina"): 15,
        (2, "jantar", "Fruta da época"): 10,
        
        # Quarta - Almoço
        (3, "almoço", "Lasanha vegetariana"): 105,  # Histórico: 100 (+5%)
        (3, "almoço", "Salmão grelhado com legumes"): 60,  # Histórico: 60 (0%)
        (3, "almoço", "Ensopado de Peru com Legumes"): 40,  # Histórico: 40 (0%)
        (3, "almoço", "Quiche de Espinafre e Queijo"): 45,
        # Quarta - Jantar
        (3, "jantar", "Creme de abóbora com pão"): 79,  # Histórico: 78 (+1.3%)
        (3, "jantar", "Massa com molho de tomate"): 51,  # Histórico: 52 (-1.9%)
        (3, "jantar", "Iogurte com Pera e Laranja"): 15,
        (3, "jantar", "Frango Grelhado com Cenoura"): 10,
        
        # Quinta - Almoço
        (4, "almoço", "Carne de vaca estufada com batatas"): 94,  # Histórico: 92 (+2.2%)
        (4, "almoço", "Peru assado com batata doce"): 54,  # Histórico: 56 (-3.6%)
        (4, "almoço", "Arroz de frango"): 37,  # Histórico: 37 (0%)
        (4, "almoço", "Bacalhau à Brás com Abóbora"): 53,
        # Quinta - Jantar
        (4, "jantar", "Pizza vegetariana"): 70,  # Histórico: 69 (+1.4%)
        (4, "jantar", "Sopa de legumes e sanduíche"): 32,  # Histórico: 46 ⚠️ (-30.4% ALERTA)
        (4, "jantar", "Salada de atum"): 18,
        (4, "jantar", "Pudim de leite"): 12,
        
        # Sexta - Almoço
        (5, "almoço", "Salmão grelhado com legumes"): 86,  # Histórico: 85 (+1.2%)
        (5, "almoço", "Frango grelhado com batata e legumes"): 50,  # Histórico: 51 (-2%)
        (5, "almoço", "Lasanha vegetariana"): 34,  # Histórico: 34 (0%)
        (5, "almoço", "Frango ao Leite com Abóbora"): 42,
        # Sexta - Jantar
        (5, "jantar", "Wrap de frango com salada"): 60,  # Histórico: 60 (0%)
        (5, "jantar", "Salada completa com frango"): 41,  # Histórico: 40 (+2.5%)
        (5, "jantar", "Pão com queijo"): 12,
        (5, "jantar", "Fruta fresca"): 8,
    }
    
    # Criar reservas para cada refeição
    # Mapa de totais por dia e tipo para fallback inteligente
    totais_por_dia_tipo = {
        ("segunda", "almoço"): 180,
        ("segunda", "jantar"): 120,
        ("terca", "almoço"): 190,
        ("terca", "jantar"): 110,
        ("quarta", "almoço"): 200,
        ("quarta", "jantar"): 130,
        ("quinta", "almoço"): 185,
        ("quinta", "jantar"): 115,
        ("sexta", "almoço"): 170,
        ("sexta", "jantar"): 100,
    }
    
    dias_semana_map = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
    
    for ref in refeicoes:
        key = (ref.dia_semana, ref.tipo, ref.descricao)
        quantidade = quantidades_por_tipo.get(key)
        
        # Se não encontrar no dicionário específico, usar fallback inteligente
        if quantidade is None:
            dia_nome = dias_semana_map[ref.dia_semana - 1] if ref.dia_semana <= 7 else "segunda"
            total_dia = totais_por_dia_tipo.get((dia_nome, ref.tipo), 150)
            quantidade = int(total_dia / 3)  # Dividir por 3 (3 opções de prato normalmente)
        
        for i in range(quantidade):
            reservas.append(ReservaRefeicaoORM(
                utilizador_id=aluno1.id if i % 2 == 0 else aluno2.id,
                refeicao_id=ref.id,
                quantidade_pessoas=1
            ))
    
    for reserva in reservas:
        session.add(reserva)
    
    session.commit()
    print(f"✅ {len(reservas)} reservas criadas para {len(refeicoes)} refeições")

def create_historico(session):
    """Criar dados históricos - versão com dados fixos que funcionam bem"""
    print("\n📊 Criando histórico...")
    
    # Histórico de refeições por dia da semana
    historico_dias = [
        HistoricoRefeicoesDiaORM(dia_semana="segunda", tipo_refeicao="almoço", total_refeicoes=180),
        HistoricoRefeicoesDiaORM(dia_semana="segunda", tipo_refeicao="jantar", total_refeicoes=120),
        HistoricoRefeicoesDiaORM(dia_semana="terca", tipo_refeicao="almoço", total_refeicoes=190),
        HistoricoRefeicoesDiaORM(dia_semana="terca", tipo_refeicao="jantar", total_refeicoes=110),
        HistoricoRefeicoesDiaORM(dia_semana="quarta", tipo_refeicao="almoço", total_refeicoes=200),
        HistoricoRefeicoesDiaORM(dia_semana="quarta", tipo_refeicao="jantar", total_refeicoes=130),
        HistoricoRefeicoesDiaORM(dia_semana="quinta", tipo_refeicao="almoço", total_refeicoes=185),
        HistoricoRefeicoesDiaORM(dia_semana="quinta", tipo_refeicao="jantar", total_refeicoes=115),
        HistoricoRefeicoesDiaORM(dia_semana="sexta", tipo_refeicao="almoço", total_refeicoes=170),
        HistoricoRefeicoesDiaORM(dia_semana="sexta", tipo_refeicao="jantar", total_refeicoes=100),
    ]
    
    for hist in historico_dias:
        session.add(hist)
    
    # Histórico de reservas por prato - com dados fixos que funcionam bem
    historico_pratos = [
        # Segunda - Almoço
        HistoricoReservasPratoORM(dia_semana="segunda", tipo_refeicao="almoço", descricao_prato="Frango grelhado com batata e legumes", total_reservas=90, percentual_escolha=0.50),
        HistoricoReservasPratoORM(dia_semana="segunda", tipo_refeicao="almoço", descricao_prato="Peixe com arroz e salada", total_reservas=54, percentual_escolha=0.30),
        HistoricoReservasPratoORM(dia_semana="segunda", tipo_refeicao="almoço", descricao_prato="Sopa de legumes e sanduíche", total_reservas=36, percentual_escolha=0.20),
        # Segunda - Jantar
        HistoricoReservasPratoORM(dia_semana="segunda", tipo_refeicao="jantar", descricao_prato="Sopa de peixe", total_reservas=72, percentual_escolha=0.60),
        HistoricoReservasPratoORM(dia_semana="segunda", tipo_refeicao="jantar", descricao_prato="Omelete com salada", total_reservas=48, percentual_escolha=0.40),
        # Terça - Almoço
        HistoricoReservasPratoORM(dia_semana="terca", tipo_refeicao="almoço", descricao_prato="Peixe assado com arroz", total_reservas=95, percentual_escolha=0.50),
        HistoricoReservasPratoORM(dia_semana="terca", tipo_refeicao="almoço", descricao_prato="Carne de vaca com batata", total_reservas=57, percentual_escolha=0.30),
        HistoricoReservasPratoORM(dia_semana="terca", tipo_refeicao="almoço", descricao_prato="Lasanha vegetariana", total_reservas=38, percentual_escolha=0.20),
        # Terça - Jantar
        HistoricoReservasPratoORM(dia_semana="terca", tipo_refeicao="jantar", descricao_prato="Salada completa com frango", total_reservas=66, percentual_escolha=0.60),
        HistoricoReservasPratoORM(dia_semana="terca", tipo_refeicao="jantar", descricao_prato="Sopa de peixe", total_reservas=44, percentual_escolha=0.40),
        # Quarta - Almoço
        HistoricoReservasPratoORM(dia_semana="quarta", tipo_refeicao="almoço", descricao_prato="Lasanha vegetariana", total_reservas=100, percentual_escolha=0.50),
        HistoricoReservasPratoORM(dia_semana="quarta", tipo_refeicao="almoço", descricao_prato="Salmão grelhado com legumes", total_reservas=60, percentual_escolha=0.30),
        HistoricoReservasPratoORM(dia_semana="quarta", tipo_refeicao="almoço", descricao_prato="Ensopado de Peru com Legumes", total_reservas=40, percentual_escolha=0.20),
        # Quarta - Jantar
        HistoricoReservasPratoORM(dia_semana="quarta", tipo_refeicao="jantar", descricao_prato="Creme de abóbora com pão", total_reservas=78, percentual_escolha=0.60),
        HistoricoReservasPratoORM(dia_semana="quarta", tipo_refeicao="jantar", descricao_prato="Massa com molho de tomate", total_reservas=52, percentual_escolha=0.40),
        # Quinta - Almoço
        HistoricoReservasPratoORM(dia_semana="quinta", tipo_refeicao="almoço", descricao_prato="Carne de vaca estufada com batatas", total_reservas=92, percentual_escolha=0.50),
        HistoricoReservasPratoORM(dia_semana="quinta", tipo_refeicao="almoço", descricao_prato="Peru assado com batata doce", total_reservas=56, percentual_escolha=0.30),
        HistoricoReservasPratoORM(dia_semana="quinta", tipo_refeicao="almoço", descricao_prato="Quiche de Espinafre e Queijo", total_reservas=37, percentual_escolha=0.20),
        # Quinta - Jantar
        HistoricoReservasPratoORM(dia_semana="quinta", tipo_refeicao="jantar", descricao_prato="Pizza vegetariana", total_reservas=69, percentual_escolha=0.60),
        HistoricoReservasPratoORM(dia_semana="quinta", tipo_refeicao="jantar", descricao_prato="Sopa de legumes e sanduíche", total_reservas=46, percentual_escolha=0.40),
        # Sexta - Almoço
        HistoricoReservasPratoORM(dia_semana="sexta", tipo_refeicao="almoço", descricao_prato="Salmão grelhado com legumes", total_reservas=85, percentual_escolha=0.50),
        HistoricoReservasPratoORM(dia_semana="sexta", tipo_refeicao="almoço", descricao_prato="Frango grelhado com batata e legumes", total_reservas=51, percentual_escolha=0.30),
        HistoricoReservasPratoORM(dia_semana="sexta", tipo_refeicao="almoço", descricao_prato="Lasanha vegetariana", total_reservas=34, percentual_escolha=0.20),
        # Sexta - Jantar
        HistoricoReservasPratoORM(dia_semana="sexta", tipo_refeicao="jantar", descricao_prato="Wrap de frango com salada", total_reservas=60, percentual_escolha=0.60),
        HistoricoReservasPratoORM(dia_semana="sexta", tipo_refeicao="jantar", descricao_prato="Salada completa com frango", total_reservas=40, percentual_escolha=0.40),
    ]
    
    for hist in historico_pratos:
        session.add(hist)
    
    session.commit()
    print(f"✅ {len(historico_dias)} registros de dias e {len(historico_pratos)} registros de pratos criados")
    
    session.commit()
    print(f"✅ {len(historico_dias)} registros de dias e {len(historico_pratos)} registros de pratos criados")

def create_execucoes(session):

    def ajustar_semana_10_sem_receitas(session):
        """Remove principais ingredientes da semana 10 para teste de falta de produtos"""
        print("\n🔧 Ajustando semana 10 para não ter produtos adequados...")
    
        # Produtos críticos para receitas que vamos remover da semana 10
        produtos_criticos = [
            "Frango", "Cenoura", "Ovos", "Queijo", "Leite",
            "Carne de Vaca", "Peru", "Peixe", "Bacalhau"
        ]
    
        produtos = session.query(ProdutoORM).filter(
            ProdutoORM.nome.in_(produtos_criticos)
        ).all()
    
        contador = 0
        for produto in produtos:
            # Obter todos os ProdutoFornecedor deste produto
            pf_list = session.query(ProdutoFornecedorORM).filter_by(
                produto_id=produto.id
            ).all()
        
            for pf in pf_list:
                # Se cobre semana 10, remover essa semana
                if pf.semana_producao_inicio <= 10 <= pf.semana_producao_fim:
                    # Se é ano-todo (1-52), dividir em duas faixas
                    if pf.semana_producao_inicio == 1 and pf.semana_producao_fim == 52:
                        pf.semana_producao_fim = 9
                        contador += 1
                        # Criar segunda entrada para semanas 11-52
                        pf2 = ProdutoFornecedorORM(
                            fornecedor_id=pf.fornecedor_id,
                            produto_id=pf.produto_id,
                            biologico=pf.biologico,
                            semana_producao_inicio=11,
                            semana_producao_fim=52,
                            capacidade=pf.capacidade,
                            unidade_medida=pf.unidade_medida,
                            data_inscricao=pf.data_inscricao
                        )
                        session.add(pf2)
                    elif pf.semana_producao_inicio <= 10 <= pf.semana_producao_fim:
                        # Outro padrão (não ano-todo), apenas remover a semana
                        # Se começa antes de 10, terminar em 9
                        if pf.semana_producao_inicio < 10:
                            pf.semana_producao_fim = 9
                            contador += 1
                            # Criar segunda entrada para semanas 11+
                            if pf.semana_producao_fim > 10:
                                pf2 = ProdutoFornecedorORM(
                                    fornecedor_id=pf.fornecedor_id,
                                    produto_id=pf.produto_id,
                                    biologico=pf.biologico,
                                    semana_producao_inicio=11,
                                    semana_producao_fim=pf.semana_producao_fim,
                                    capacidade=pf.capacidade,
                                    unidade_medida=pf.unidade_medida,
                                    data_inscricao=pf.data_inscricao
                                )
                                session.add(pf2)
                        # Se começa em 10 ou depois, apenas deletar
                        elif pf.semana_producao_inicio == 10:
                            session.delete(pf)
                            contador += 1
    
        session.commit()
        print(f"✅ Semana 10 ajustada: {contador} registros modificados")
    """Criar dados de execução de refeições para teste de desperdício"""
    print("\n⚙️  Criando execuções de refeições...")
    
    today = date.today()
    
    # Buscar algumas refeições para criar execuções
    refeicoes = session.query(RefeicaoORM).limit(14).all()
    
    execucoes = []
    for idx, refeicao in enumerate(refeicoes):
        # Simular dados de execução
        # Refeições têm diferentes níveis de desperdício
        if idx % 3 == 0:  # 33% com pouco desperdício
            prod = 100
            serv = 95
            nao_serv = 5
        elif idx % 3 == 1:  # 33% com desperdício médio
            prod = 100
            serv = 80
            nao_serv = 20
        else:  # 33% com desperdício alto
            prod = 100
            serv = 65
            nao_serv = 35
        
        exec_refeicao = ExecucaoRefeicaoORM(
            refeicao_id=refeicao.id,
            data_execucao=today - timedelta(days=1),
            quantidade_produzida=prod,
            quantidade_servida=serv,
            quantidade_nao_servida=nao_serv
        )
        execucoes.append(exec_refeicao)
        session.add(exec_refeicao)
    
    session.commit()
    print(f"✅ {len(execucoes)} execuções de refeições criadas")

def main():
    print("=" * 70)
    print("🔄 RECRIANDO BANCO DE DADOS COMPLETO - SEM DUPLICADOS")
    print("=" * 70)
    
    # Usar o mesmo caminho que o backend
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # scripts -> projeto raiz
    DB_FILE = PROJECT_ROOT / "biocantinas.db"
    DB_PATH = f"sqlite:///{DB_FILE}"
    
    print(f"\n📍 Base de dados: {DB_FILE}\n")
    
    delete_database(DB_PATH)
    
    # Recriar o engine para garantir que não há cache
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    new_engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
    
    print("\n📦 Criando tabelas...")
    Base.metadata.create_all(bind=new_engine)
    print("✅ Tabelas criadas")
    
    SessionFactory = sessionmaker(bind=new_engine, autoflush=False, autocommit=False)
    session = SessionFactory()
    
    try:
        user_ids = create_users(session)
        create_fornecedores(session, user_ids)
        create_receitas(session)
        create_ementas(session)
        create_reservas(session)
        create_historico(session)
        create_execucoes(session)
        
        print("\n" + "=" * 70)
        print("✅ BANCO DE DADOS RECRIADO COM SUCESSO!")
        print("=" * 70)
        print("\n📊 Resumo:")
        print(f"  - Usuários: {session.query(UserORM).count()}")
        print(f"  - Fornecedores: {session.query(FornecedorORM).count()}")
        print(f"  - Produtos: {session.query(ProdutoFornecedorORM).count()}")
        print(f"  - Receitas: {session.query(ReceitaORM).count()}")
        print(f"  - Ementas: {session.query(EmentaORM).count()}")
        print(f"  - Refeições: {session.query(RefeicaoORM).count()}")
        print(f"  - Reservas: {session.query(ReservaRefeicaoORM).count()}")
        print(f"  - Execuções: {session.query(ExecucaoRefeicaoORM).count()}")
        print(f"  - Histórico Dias: {session.query(HistoricoRefeicoesDiaORM).count()}")
        print(f"  - Histórico Pratos: {session.query(HistoricoReservasPratoORM).count()}")
        
        print("\n👤 Credenciais:")
        print("  - Gestor Cantina: gestor / 1")
        print("  - Dietista: dietista / 1")
        print("  - Aluno 1: aluno1 / 1")
        print("  - Aluno 2: aluno2 / 1")
        print("  - João Silva (Produtor): João Silva / 1")
        print("  - Maria Carvalho (Produtora): Maria Carvalho / 1")
        
        # Copiar o banco de dados para o diretório do backend
        import shutil
        db_origem = Path(__file__).parent.parent / "biocantinas.db"
        db_destino = Path(__file__).parent.parent / "biocantinas" / "backend" / "biocantinas.db"
        
        if db_origem.exists():
            print(f"\n📋 Copiando banco de dados para {db_destino}")
            shutil.copy2(db_origem, db_destino)
            print("✅ Banco de dados copiado com sucesso!")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
