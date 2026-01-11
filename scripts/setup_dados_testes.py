"""
SETUP DE DADOS PARA TESTES
Consolidado em um único ficheiro com:
1. Criação de ementas baseadas em receitas do catálogo
2. Criação de planos de produção
3. Criação de execuções de teste
"""

import sys
sys.path.insert(0, r"d:\ENGREQ\ENGREQ_Biocantinas_1241928_1211622\biocantinas\backend")

from datetime import date, timedelta
from app.db.models import (
    EmentaORM, RefeicaoORM, ItemRefeicaoORM, 
    ReceitaORM, PlanoProducaoORM, ExecucaoRefeicaoORM,
    ItemReceitaORM, ProdutoORM
)
from app.db.session import SessionLocal, init_db
import json

init_db()
session = SessionLocal()

print("=" * 70)
print("📋 SETUP DE DADOS PARA TESTES - CONSOLIDADO")
print("=" * 70)

# ============================================
# 1. OBTER RECEITAS DO CATÁLOGO
# ============================================
print("\n🍽️  Buscando receitas do catálogo...")
receitas = session.query(ReceitaORM).filter(ReceitaORM.ativa == True).all()
print(f"✅ {len(receitas)} receitas ativas encontradas")

if not receitas:
    print("❌ Nenhuma receita encontrada! Execute recreate_full_db.py primeiro.")
    session.close()
    exit(1)

# ============================================
# 2. LIMPAR EMENTAS ANTIGAS (opcional)
# ============================================
print("\n🧹 Limpando ementas antigas...")
num_ementas_antigas = session.query(EmentaORM).count()
session.query(EmentaORM).delete()
print(f"✅ {num_ementas_antigas} ementas antigas removidas")

# ============================================
# 3. CRIAR EMENTAS COM RECEITAS DO CATÁLOGO
# ============================================
print("\n📋 Criando ementas baseadas em receitas...")

# Semana de teste: 05 a 09 de Jan 2026 (segunda a sexta)
monday = date(2026, 1, 5)
friday = date(2026, 1, 9)

# Criar ementa
ementa = EmentaORM(
    nome=f"Semana de {monday.strftime('%d/%m')} a {friday.strftime('%d/%m/%Y')}",
    data_inicio=monday,
    data_fim=friday
)
session.add(ementa)
session.flush()  # Para obter o ID

print(f"  ✅ Ementa '{ementa.nome}' criada")

# Criar refeições usando receitas do catálogo
dias_semana = {
    1: ("Segunda", "Monday"),
    2: ("Terça", "Tuesday"),
    3: ("Quarta", "Wednesday"),
    4: ("Quinta", "Thursday"),
    5: ("Sexta", "Friday")
}

refeicoes_criadas = 0

for dia_num in range(1, 6):  # Segunda a Sexta
    dia_nome_pt, _ = dias_semana[dia_num]
    
    # Escolher 2 receitas aleatoriamente para almoço e jantar
    receita_almoco = receitas[dia_num - 1] if dia_num <= len(receitas) else receitas[0]
    receita_jantar = receitas[(dia_num + len(receitas)//2 - 1) % len(receitas)]
    
    # ALMOÇO
    refeicao_almoco = RefeicaoORM(
        ementa_id=ementa.id,
        receita_id=receita_almoco.id,
        dia_semana=dia_num,
        tipo="almoço",
        descricao=receita_almoco.nome,
        numero_porcoes=100
    )
    session.add(refeicao_almoco)
    session.flush()
    
    # Copiar ingredientes da receita
    for item_receita in receita_almoco.ingredientes:
        item_refeicao = ItemRefeicaoORM(
            refeicao_id=refeicao_almoco.id,
            ingrediente=item_receita.produto.nome if item_receita.produto else "Desconhecido",
            quantidade_estimada=item_receita.quantidade_por_porcao
        )
        session.add(item_refeicao)
    
    refeicoes_criadas += 1
    print(f"  ✅ {dia_nome_pt} Almoço: {receita_almoco.nome}")
    
    # JANTAR
    refeicao_jantar = RefeicaoORM(
        ementa_id=ementa.id,
        receita_id=receita_jantar.id,
        dia_semana=dia_num,
        tipo="jantar",
        descricao=receita_jantar.nome,
        numero_porcoes=100
    )
    session.add(refeicao_jantar)
    session.flush()
    
    # Copiar ingredientes da receita
    for item_receita in receita_jantar.ingredientes:
        item_refeicao = ItemRefeicaoORM(
            refeicao_id=refeicao_jantar.id,
            ingrediente=item_receita.produto.nome if item_receita.produto else "Desconhecido",
            quantidade_estimada=item_receita.quantidade_por_porcao
        )
        session.add(item_refeicao)
    
    refeicoes_criadas += 1
    print(f"  ✅ {dia_nome_pt} Jantar: {receita_jantar.nome}")

session.commit()
print(f"\n✅ Total de {refeicoes_criadas} refeições criadas")

# ============================================
# 4. CRIAR PLANOS DE PRODUÇÃO
# ============================================
print("\n📊 Criando planos de produção...")

# Limpar planos antigos
session.query(PlanoProducaoORM).filter(
    PlanoProducaoORM.periodo_data_inicio == monday,
    PlanoProducaoORM.periodo_data_fim == friday,
).delete()

# Extrair produtos únicos das receitas e gerar planos
produtos_plano = {
    "Frango": 25,
    "Carne de Vaca": 20,
    "Peixe Grelhado": 15,
    "Bacalhau Simples": 15,
    "Peru": 12,
    "Ovos": 250,
    "Cenoura": 60,
    "Batata": 90,
    "Salada": 30,
    "Omeleta": 20,
    "Beterraba": 20,
    "Couve": 25,
    "Sopa": 30,
    "Alface": 25,
    "Tomate": 45
}

for produto_nome, quantidade in produtos_plano.items():
    plano = PlanoProducaoORM(
        periodo_data_inicio=monday,
        periodo_data_fim=friday,
        produto_nome=produto_nome,
        quantidade_prevista=quantidade,
        quantidade_realizada=0,
        desvio_percentual=0.0,
        requer_alerta=False
    )
    session.add(plano)
    print(f"  ✅ {produto_nome}: {quantidade} unidade(s)")

session.commit()
print(f"\n✅ {len(produtos_plano)} planos de produção criados")

# ============================================
# 5. CRIAR EXECUÇÕES DE REFEIÇÕES PARA TESTE
# ============================================
print("\n⚙️  Criando execuções de refeições para teste...")

# Obter refeições criadas
refeicoes = session.query(RefeicaoORM).filter(
    RefeicaoORM.ementa_id == ementa.id
).all()

data_execucao = date(2026, 1, 10)  # Sábado (dia para registrar execuções)

execucoes_criadas = 0
for refeicao in refeicoes:
    # Simular: produzidas 100, servidas 90, não servidas 10
    execucao = ExecucaoRefeicaoORM(
        refeicao_id=refeicao.id,
        data_execucao=data_execucao,
        quantidade_prevista=100,
        quantidade_produzida=100,
        quantidade_servida=90,
        quantidade_nao_servida=10
    )
    session.add(execucao)
    execucoes_criadas += 1

session.commit()
print(f"✅ {execucoes_criadas} execuções criadas para {data_execucao}")

# ============================================
# 6. RESUMO FINAL
# ============================================
print("\n" + "=" * 70)
print("✅ SETUP DE DADOS PARA TESTES CONCLUÍDO")
print("=" * 70)

print(f"\n📊 Resumo:")
print(f"  - Ementas criadas: 1")
print(f"  - Refeições criadas: {refeicoes_criadas}")
print(f"  - Planos de produção: {len(produtos_plano)}")
print(f"  - Execuções de teste: {execucoes_criadas}")

print(f"\n📅 Período de teste:")
print(f"  - Ementa: {monday} a {friday} (Segunda a Sexta)")
print(f"  - Execuções: {data_execucao} (Sábado)")

print(f"\n💡 Para testar o relatório:")
print(f"  1. Aceda a: http://localhost:8501")
print(f"  2. Navegue para: Gestor Cantina → Comparação Realizado vs Previsto")
print(f"  3. Selecione: {monday} a {data_execucao}")
print(f"  4. Clique em: Gerar Relatório")

session.close()
print("\n✅ Script concluído com sucesso!")
