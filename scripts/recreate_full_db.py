"""
Script para RECRIAR completamente o banco de dados
Remove e cria tudo do zero com dados completos
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from datetime import date, timedelta
from biocantinas.backend.app.db.session import SessionLocal, engine, init_db
from biocantinas.backend.app.db.models import (
    Base, UserORM, FornecedorORM, ProdutoFornecedorORM, 
    EmentaORM, RefeicaoORM, ItemRefeicaoORM, ReservaRefeicaoORM,
    HistoricoRefeicoesDiaORM, HistoricoReservasPratoORM, ExecucaoRefeicaoORM
)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def delete_database(db_url: str):
    """Remove arquivos de banco de dados (principal e cb4pia do backend)"""
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
        UserORM(
            username="gestor",
            hashed_password=pwd_context.hash("1"),
            role="GESTOR_CANTINA",
            is_active=True
        ),
        UserORM(
            username="dietista",
            hashed_password=pwd_context.hash("1"),
            role="DIETISTA",
            is_active=True
        ),
        UserORM(
            username="aluno1",
            hashed_password=pwd_context.hash("1"),
            role="ALUNO",
            is_active=True
        ),
        UserORM(
            username="aluno2",
            hashed_password=pwd_context.hash("1"),
            role="ALUNO",
            is_active=True
        ),
        UserORM(
            username="joao",
            hashed_password=pwd_context.hash("1"),
            role="PRODUTOR",
            is_active=True
        ),
        UserORM(
            username="maria",
            hashed_password=pwd_context.hash("1"),
            role="PRODUTOR",
            is_active=True
        ),
        UserORM(
            username="pedro",
            hashed_password=pwd_context.hash("1"),
            role="PRODUTOR",
            is_active=True
        ),
        UserORM(
            username="ana",
            hashed_password=pwd_context.hash("1"),
            role="PRODUTOR",
            is_active=True
        ),
        UserORM(
            username="carlos",
            hashed_password=pwd_context.hash("1"),
            role="PRODUTOR",
            is_active=True
        ),
        UserORM(
            username="lucas",
            hashed_password=pwd_context.hash("1"),
            role="PRODUTOR",
            is_active=True
        ),
    ]
    
    for user in users:
        session.add(user)
    session.commit()
    print(f"✅ {len(users)} usuários criados")
    
    # Return users for linking with suppliers
    return {user.username: user.id for user in users}

def create_fornecedores(session, user_ids):
    """Criar fornecedores e seus produtos"""
    print("\n🚜 Criando fornecedores...")
    
    today = date.today()
    
    # Fornecedores vinculados aos usuários produtores via usuario_id
    fornecedores_data = [
        # João - Frutas variadas
        {
            "nome": "João Silva Frutas",
            "usuario_id": user_ids["joao"],
            "data_inscricao": today - timedelta(days=30),
            "aprovado": True,
            "produtos": [
                {"nome": "Maçã", "tipo": "Fruta", "inicio": today, "fim": today + timedelta(days=90), "capacidade": 100, "biologico": True},
                {"nome": "Pera", "tipo": "Fruta", "inicio": today, "fim": today + timedelta(days=60), "capacidade": 50, "biologico": True},
                {"nome": "Laranja", "tipo": "Fruta", "inicio": today, "fim": today + timedelta(days=120), "capacidade": 80, "biologico": True},
            ]
        },
        # Maria - Hortícolas
        {
            "nome": "Maria Carvalho Hortas",
            "usuario_id": user_ids["maria"],
            "data_inscricao": today - timedelta(days=35),
            "aprovado": True,
            "produtos": [
                {"nome": "Tomate", "tipo": "Hortícola", "inicio": today, "fim": today + timedelta(days=40), "capacidade": 100, "biologico": True},
                {"nome": "Alface", "tipo": "Hortícola", "inicio": today, "fim": today + timedelta(days=20), "capacidade": 40, "biologico": True},
                {"nome": "Cenoura", "tipo": "Hortícola", "inicio": today, "fim": today + timedelta(days=120), "capacidade": 80, "biologico": True},
                {"nome": "Couve", "tipo": "Hortícola", "inicio": today, "fim": today + timedelta(days=30), "capacidade": 50, "biologico": True},
            ]
        },
        # Pedro - Proteínas
        {
            "nome": "Pedro Santos Carnes",
            "usuario_id": user_ids["pedro"],
            "data_inscricao": today - timedelta(days=25),
            "aprovado": True,
            "produtos": [
                {"nome": "Frango", "tipo": "Proteína", "inicio": today, "fim": today + timedelta(days=365), "capacidade": 300, "biologico": True},
                {"nome": "Carne de Vaca", "tipo": "Proteína", "inicio": today, "fim": today + timedelta(days=365), "capacidade": 250, "biologico": True},
                {"nome": "Ovos", "tipo": "Proteína", "inicio": today, "fim": today + timedelta(days=365), "capacidade": 500, "biologico": True},
            ]
        },
        # Ana - Cereais e Laticínios
        {
            "nome": "Ana Costa Cereais e Lacticínios",
            "usuario_id": user_ids["ana"],
            "data_inscricao": today - timedelta(days=20),
            "aprovado": True,
            "produtos": [
                {"nome": "Arroz", "tipo": "Cereais", "inicio": today, "fim": today + timedelta(days=365), "capacidade": 200, "biologico": True},
                {"nome": "Massa", "tipo": "Cereais", "inicio": today, "fim": today + timedelta(days=365), "capacidade": 150, "biologico": True},
                {"nome": "Leite", "tipo": "Laticínios", "inicio": today, "fim": today + timedelta(days=365), "capacidade": 300, "biologico": True},
                {"nome": "Queijo", "tipo": "Laticínios", "inicio": today, "fim": today + timedelta(days=365), "capacidade": 100, "biologico": True},
            ]
        },
        # Carlos - Mix de produtos
        {
            "nome": "Carlos Ribeiro Agrobio",
            "usuario_id": user_ids["carlos"],
            "data_inscricao": today - timedelta(days=15),
            "aprovado": True,
            "produtos": [
                {"nome": "Batata", "tipo": "Hortícola", "inicio": today, "fim": today + timedelta(days=150), "capacidade": 150, "biologico": True},
                {"nome": "Banana", "tipo": "Fruta", "inicio": today, "fim": today + timedelta(days=90), "capacidade": 70, "biologico": True},
                {"nome": "Peixe", "tipo": "Proteína", "inicio": today, "fim": today + timedelta(days=365), "capacidade": 120, "biologico": True},
                {"nome": "Pão", "tipo": "Cereais", "inicio": today, "fim": today + timedelta(days=365), "capacidade": 200, "biologico": True},
                {"nome": "Iogurte", "tipo": "Laticínios", "inicio": today, "fim": today + timedelta(days=365), "capacidade": 150, "biologico": True},
            ]
        },
        # Lucas - Produtor de Frango (menor prioridade - registro mais recente)
        {
            "nome": "Lucas Ferreira Aves",
            "usuario_id": user_ids["lucas"],
            "data_inscricao": today - timedelta(days=10),
            "aprovado": True,
            "produtos": [
                {"nome": "Frango", "tipo": "Proteína", "inicio": today, "fim": today + timedelta(days=365), "capacidade": 150, "biologico": True},
            ]
        },
    ]
    
    for data in fornecedores_data:
        fornecedor = FornecedorORM(
            nome=data["nome"],
            usuario_id=data["usuario_id"],
            data_inscricao=data["data_inscricao"],
            aprovado=data["aprovado"]
        )
        session.add(fornecedor)
        session.flush()
        
        for p in data["produtos"]:
            produto = ProdutoFornecedorORM(
                fornecedor_id=fornecedor.id,
                nome=p['nome'],
                tipo=p['tipo'],
                biologico=p['biologico'],
                intervalo_producao_inicio=p['inicio'],
                intervalo_producao_fim=p['fim'],
                capacidade=p['capacidade']
            )
            session.add(produto)
    
    session.commit()
    print(f"✅ {len(fornecedores_data)} fornecedores criados")

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
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=1,
            tipo="almoço",
            descricao="Frango grelhado com batata e legumes",
            itens=[
                ItemRefeicaoORM(ingrediente="frango", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=3),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=2),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=1,
            tipo="jantar",
            descricao="Sopa de legumes e sanduíche",
            itens=[
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=1),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="couve", quantidade_estimada=1),
            ]
        ),
        # TERÇA-FEIRA (dia_semana=2) - 10 Dez
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=2,
            tipo="almoço",
            descricao="Peixe assado com arroz",
            itens=[
                ItemRefeicaoORM(ingrediente="pescada", quantidade_estimada=3),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="beterraba", quantidade_estimada=1),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=2,
            tipo="jantar",
            descricao="Salada completa com frango",
            itens=[
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=1),
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=1),
                ItemRefeicaoORM(ingrediente="frango", quantidade_estimada=2),
            ]
        ),
        # QUARTA-FEIRA (dia_semana=3) - 11 Dez
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=3,
            tipo="almoço",
            descricao="Lasanha vegetariana",
            itens=[
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="queijo", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="espinafre", quantidade_estimada=1),
                ItemRefeicaoORM(ingrediente="curgete", quantidade_estimada=1),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=3,
            tipo="jantar",
            descricao="Creme de abóbora com pão",
            itens=[
                ItemRefeicaoORM(ingrediente="batata doce", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=1),
            ]
        ),
        # QUINTA-FEIRA (dia_semana=4) - 12 Dez
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=4,
            tipo="almoço",
            descricao="Carne de vaca estufada com batatas",
            itens=[
                ItemRefeicaoORM(ingrediente="carne de vaca", quantidade_estimada=3),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=3),
                ItemRefeicaoORM(ingrediente="cenoura", quantidade_estimada=1),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=4,
            tipo="jantar",
            descricao="Pizza vegetariana",
            itens=[
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="queijo", quantidade_estimada=1),
                ItemRefeicaoORM(ingrediente="pimento", quantidade_estimada=1),
            ]
        ),
        # SEXTA-FEIRA (dia_semana=5) - 13 Dez
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=5,
            tipo="almoço",
            descricao="Salmão grelhado com legumes",
            itens=[
                ItemRefeicaoORM(ingrediente="salmão", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="beterraba", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="couve", quantidade_estimada=1),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa1.id,
            dia_semana=5,
            tipo="jantar",
            descricao="Wrap de frango com salada",
            itens=[
                ItemRefeicaoORM(ingrediente="frango", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=1),
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=1),
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
                ItemRefeicaoORM(ingrediente="peru", quantidade_estimada=3),
                ItemRefeicaoORM(ingrediente="batata doce", quantidade_estimada=2),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa2.id,
            dia_semana=1,
            tipo="jantar",
            descricao="Sopa de peixe",
            itens=[
                ItemRefeicaoORM(ingrediente="pescada", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=2),
            ]
        ),
        # TERÇA-FEIRA (dia_semana=2) - 17 Dez
        RefeicaoORM(
            ementa_id=ementa2.id,
            dia_semana=2,
            tipo="almoço",
            descricao="Bacalhau com natas",
            itens=[
                ItemRefeicaoORM(ingrediente="bacalhau", quantidade_estimada=2),
                ItemRefeicaoORM(ingrediente="batata", quantidade_estimada=3),
                ItemRefeicaoORM(ingrediente="queijo", quantidade_estimada=1),
            ]
        ),
        RefeicaoORM(
            ementa_id=ementa2.id,
            dia_semana=2,
            tipo="jantar",
            descricao="Salada de atum",
            itens=[
                ItemRefeicaoORM(ingrediente="alface", quantidade_estimada=1),
                ItemRefeicaoORM(ingrediente="tomate", quantidade_estimada=1),
            ]
        ),
    ]
    
    for refeicao in refeicoes2:
        session.add(refeicao)
    
    session.commit()
    print(f"✅ 2 ementas criadas com {len(refeicoes1) + len(refeicoes2)} refeições")

def create_reservas(session):
    """Criar reservas de alunos"""
    print("\n📝 Criando reservas...")
    
    aluno1 = session.query(UserORM).filter_by(username="aluno1").first()
    aluno2 = session.query(UserORM).filter_by(username="aluno2").first()
    
    refeicoes = session.query(RefeicaoORM).all()
    
    if not aluno1 or not aluno2 or len(refeicoes) < 5:
        print("⚠️  Dados insuficientes para criar reservas")
        return
    
    # Mapear refeições por dia_semana e tipo
    refeicoes_map = {}
    for ref in refeicoes:
        key = (ref.dia_semana, ref.tipo, ref.descricao)
        refeicoes_map[key] = ref
    
    reservas = []
    
    # Criar reservas simulando números similares ao histórico
    # Segunda - Almoço: Frango grelhado (90 reservas no histórico)
    ref = refeicoes_map.get((1, "almoço", "Frango grelhado com batata e legumes"))
    if ref:
        for i in range(100):  # Criar 88 reservas (simulando ~90)
            reservas.append(ReservaRefeicaoORM(
                utilizador_id=aluno1.id if i % 2 == 0 else aluno2.id,
                refeicao_id=ref.id,
                quantidade_pessoas=1
            ))
    
    # Segunda - Jantar: Sopa de legumes (72 reservas no histórico)
    ref = refeicoes_map.get((1, "jantar", "Sopa de legumes e sanduíche"))
    if ref:
        for i in range(70):
            reservas.append(ReservaRefeicaoORM(
                utilizador_id=aluno1.id if i % 2 == 0 else aluno2.id,
                refeicao_id=ref.id,
                quantidade_pessoas=1
            ))
    
    # Terça - Almoço: Peixe assado (95 reservas no histórico)
    ref = refeicoes_map.get((2, "almoço", "Peixe assado com arroz"))
    if ref:
        for i in range(92):
            reservas.append(ReservaRefeicaoORM(
                utilizador_id=aluno1.id if i % 2 == 0 else aluno2.id,
                refeicao_id=ref.id,
                quantidade_pessoas=1
            ))
    
    # Terça - Jantar: Salada com frango (66 reservas no histórico)
    ref = refeicoes_map.get((2, "jantar", "Salada completa com frango"))
    if ref:
        for i in range(50):
            reservas.append(ReservaRefeicaoORM(
                utilizador_id=aluno1.id if i % 2 == 0 else aluno2.id,
                refeicao_id=ref.id,
                quantidade_pessoas=1
            ))
    
    # Quarta - Almoço: Lasanha vegetariana (100 reservas no histórico)
    ref = refeicoes_map.get((3, "almoço", "Lasanha vegetariana"))
    if ref:
        for i in range(98):
            reservas.append(ReservaRefeicaoORM(
                utilizador_id=aluno1.id if i % 2 == 0 else aluno2.id,
                refeicao_id=ref.id,
                quantidade_pessoas=1
            ))
    
    # Quarta - Jantar: Creme de abóbora (78 reservas no histórico)
    ref = refeicoes_map.get((3, "jantar", "Creme de abóbora com pão"))
    if ref:
        for i in range(76):
            reservas.append(ReservaRefeicaoORM(
                utilizador_id=aluno1.id if i % 2 == 0 else aluno2.id,
                refeicao_id=ref.id,
                quantidade_pessoas=1
            ))
    
    # Quinta - Almoço: Carne de vaca (92 reservas no histórico)
    ref = refeicoes_map.get((4, "almoço", "Carne de vaca estufada com batatas"))
    if ref:
        for i in range(90):
            reservas.append(ReservaRefeicaoORM(
                utilizador_id=aluno1.id if i % 2 == 0 else aluno2.id,
                refeicao_id=ref.id,
                quantidade_pessoas=1
            ))
    
    # Quinta - Jantar: Pizza vegetariana (69 reservas no histórico)
    ref = refeicoes_map.get((4, "jantar", "Pizza vegetariana"))
    if ref:
        for i in range(68):
            reservas.append(ReservaRefeicaoORM(
                utilizador_id=aluno1.id if i % 2 == 0 else aluno2.id,
                refeicao_id=ref.id,
                quantidade_pessoas=1
            ))
    
    # Sexta - Almoço: Salmão (85 reservas no histórico)
    ref = refeicoes_map.get((5, "almoço", "Salmão grelhado com legumes"))
    if ref:
        for i in range(83):
            reservas.append(ReservaRefeicaoORM(
                utilizador_id=aluno1.id if i % 2 == 0 else aluno2.id,
                refeicao_id=ref.id,
                quantidade_pessoas=1
            ))
    
    # Sexta - Jantar: Wrap de frango (60 reservas no histórico)
    ref = refeicoes_map.get((5, "jantar", "Wrap de frango com salada"))
    if ref:
        for i in range(58):
            reservas.append(ReservaRefeicaoORM(
                utilizador_id=aluno1.id if i % 2 == 0 else aluno2.id,
                refeicao_id=ref.id,
                quantidade_pessoas=1
            ))
    
    for reserva in reservas:
        session.add(reserva)
    
    session.commit()
    print(f"✅ {len(reservas)} reservas criadas")

def create_historico(session):
    """Criar dados históricos"""
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
    
    # Histórico de reservas por prato
    historico_pratos = [
        # Segunda - Almoço
        HistoricoReservasPratoORM(dia_semana="segunda", tipo_refeicao="almoço", descricao_prato="Frango grelhado com batata e legumes", total_reservas=90, percentual_escolha=0.50),
        HistoricoReservasPratoORM(dia_semana="segunda", tipo_refeicao="almoço", descricao_prato="Peixe assado com arroz", total_reservas=54, percentual_escolha=0.30),
        HistoricoReservasPratoORM(dia_semana="segunda", tipo_refeicao="almoço", descricao_prato="Lasanha vegetariana", total_reservas=36, percentual_escolha=0.20),
        # Segunda - Jantar
        HistoricoReservasPratoORM(dia_semana="segunda", tipo_refeicao="jantar", descricao_prato="Sopa de legumes e sanduíche", total_reservas=72, percentual_escolha=0.60),
        HistoricoReservasPratoORM(dia_semana="segunda", tipo_refeicao="jantar", descricao_prato="Salada completa com frango", total_reservas=48, percentual_escolha=0.40),
        # Terça - Almoço
        HistoricoReservasPratoORM(dia_semana="terca", tipo_refeicao="almoço", descricao_prato="Peixe assado com arroz", total_reservas=95, percentual_escolha=0.50),
        HistoricoReservasPratoORM(dia_semana="terca", tipo_refeicao="almoço", descricao_prato="Frango grelhado com batata e legumes", total_reservas=57, percentual_escolha=0.30),
        HistoricoReservasPratoORM(dia_semana="terca", tipo_refeicao="almoço", descricao_prato="Lasanha vegetariana", total_reservas=38, percentual_escolha=0.20),
        # Terça - Jantar
        HistoricoReservasPratoORM(dia_semana="terca", tipo_refeicao="jantar", descricao_prato="Salada completa com frango", total_reservas=66, percentual_escolha=0.60),
        HistoricoReservasPratoORM(dia_semana="terca", tipo_refeicao="jantar", descricao_prato="Sopa de legumes e sanduíche", total_reservas=44, percentual_escolha=0.40),
        # Quarta - Almoço
        HistoricoReservasPratoORM(dia_semana="quarta", tipo_refeicao="almoço", descricao_prato="Lasanha vegetariana", total_reservas=100, percentual_escolha=0.50),
        HistoricoReservasPratoORM(dia_semana="quarta", tipo_refeicao="almoço", descricao_prato="Frango grelhado com batata e legumes", total_reservas=60, percentual_escolha=0.30),
        HistoricoReservasPratoORM(dia_semana="quarta", tipo_refeicao="almoço", descricao_prato="Peixe assado com arroz", total_reservas=40, percentual_escolha=0.20),
        # Quarta - Jantar
        HistoricoReservasPratoORM(dia_semana="quarta", tipo_refeicao="jantar", descricao_prato="Creme de abóbora com pão", total_reservas=78, percentual_escolha=0.60),
        HistoricoReservasPratoORM(dia_semana="quarta", tipo_refeicao="jantar", descricao_prato="Salada completa com frango", total_reservas=52, percentual_escolha=0.40),
        # Quinta - Almoço
        HistoricoReservasPratoORM(dia_semana="quinta", tipo_refeicao="almoço", descricao_prato="Carne de vaca estufada com batatas", total_reservas=92, percentual_escolha=0.50),
        HistoricoReservasPratoORM(dia_semana="quinta", tipo_refeicao="almoço", descricao_prato="Peixe assado com arroz", total_reservas=56, percentual_escolha=0.30),
        HistoricoReservasPratoORM(dia_semana="quinta", tipo_refeicao="almoço", descricao_prato="Lasanha vegetariana", total_reservas=37, percentual_escolha=0.20),
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

def create_execucoes(session):
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
    
    DB_PATH = os.getenv("BIOCANTINAS_DB_PATH", "sqlite:///biocantinas.db")
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
        print(f"  - Ementas: {session.query(EmentaORM).count()}")
        print(f"  - Refeições: {session.query(RefeicaoORM).count()}")
        print(f"  - Reservas: {session.query(ReservaRefeicaoORM).count()}")
        print(f"  - Execuções: {session.query(ExecucaoRefeicaoORM).count()}")
        print(f"  - Histórico Dias: {session.query(HistoricoRefeicoesDiaORM).count()}")
        print(f"  - Histórico Pratos: {session.query(HistoricoReservasPratoORM).count()}")
        
        print("\n👤 Credenciais:")
        print("  - Gestor: gestor_cantina / gestor123")
        print("  - Dietista: dietista / dietista123")
        print("  - Aluno 1: aluno1 / aluno123")
        print("  - Aluno 2: aluno2 / aluno123")
        print("  - João Silva (Produtor): João Silva / produtor123")
        print("  - Maria Carvalho (Produtora): Maria Carvalho / produtor123")
        
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
