from datetime import date, timedelta
from biocantinas.backend.app.db.session import SessionLocal, init_db
from biocantinas.backend.app.db.models import FornecedorORM, ProdutoFornecedorORM


def already_populated(session) -> bool:
    count = session.query(FornecedorORM).count()
    return count >= 20  # Increased threshold to ensure more suppliers


def insert_fornecedor(session, nome, data_inscricao, aprovado, produtos):
    fornecedor = FornecedorORM(
        nome=nome,
        data_inscricao=data_inscricao,
        aprovado=bool(aprovado)
    )
    session.add(fornecedor)
    session.flush()  # Get the ID without committing
    
    for p in produtos:
        produto = ProdutoFornecedorORM(
            fornecedor_id=fornecedor.id,
            nome=p['nome'],
            tipo=p.get('tipo'),
            biologico=p.get('biologico', True),  # Default True se não especificado
            intervalo_producao_inicio=p['inicio'],
            intervalo_producao_fim=p['fim'],
            capacidade=int(p.get('capacidade', 0))
        )
        session.add(produto)


def main():
    # Initialize database and create tables
    init_db()
    
    session = SessionLocal()
    
    try:
        if already_populated(session):
            print("A base já tem >= 20 fornecedores. Nenhuma ação feita.")
            return

        today = date.today()

        samples = [
            # Fornecedores de Frutas (Biológico)
            ("João Silva", today - timedelta(days=10), 1, [
                {"nome": "maçã", "tipo": "fruta", "biologico": True, "inicio": today, "fim": today + timedelta(days=90), "capacidade": 100},
                {"nome": "pera", "tipo": "fruta", "biologico": True, "inicio": today, "fim": today + timedelta(days=60), "capacidade": 50},
                {"nome": "kiwi", "tipo": "fruta", "biologico": True, "inicio": today, "fim": today + timedelta(days=60), "capacidade": 30},
            ]),
            ("Maria Oliveira", today - timedelta(days=9), 1, [
                {"nome": "morango", "tipo": "fruta", "biologico": True, "inicio": today, "fim": today + timedelta(days=30), "capacidade": 40},
                {"nome": "mirtilo", "tipo": "fruta", "biologico": True, "inicio": today, "fim": today + timedelta(days=45), "capacidade": 25},
                {"nome": "framboesa", "tipo": "fruta", "biologico": True, "inicio": today, "fim": today + timedelta(days=35), "capacidade": 20},
            ]),
            ("Pedro Santos", today - timedelta(days=9), 1, [
                {"nome": "laranja", "tipo": "fruta", "biologico": False, "inicio": today, "fim": today + timedelta(days=120), "capacidade": 80},
                {"nome": "limão", "tipo": "fruta", "biologico": False, "inicio": today, "fim": today + timedelta(days=120), "capacidade": 60},
                {"nome": "cereja", "tipo": "fruta", "biologico": True, "inicio": today, "fim": today + timedelta(days=30), "capacidade": 15},
            ]),
            ("Ana Costa", today - timedelta(days=8), 1, [
                {"nome": "banana", "tipo": "fruta", "biologico": True, "inicio": today, "fim": today + timedelta(days=90), "capacidade": 70},
                {"nome": "uva", "tipo": "fruta", "biologico": True, "inicio": today, "fim": today + timedelta(days=45), "capacidade": 35},
                {"nome": "melancia", "tipo": "fruta", "biologico": False, "inicio": today, "fim": today + timedelta(days=30), "capacidade": 50},
            ]),
            # Fornecedores de Hortícolas - Folhas (Biológico)
            ("Luís Pereira", today - timedelta(days=7), 1, [
                {"nome": "alface", "tipo": "hortícola-folha", "biologico": True, "inicio": today, "fim": today + timedelta(days=20), "capacidade": 40},
                {"nome": "rúcula", "tipo": "hortícola-folha", "biologico": True, "inicio": today, "fim": today + timedelta(days=15), "capacidade": 25},
                {"nome": "espinafre", "tipo": "hortícola-folha", "biologico": True, "inicio": today, "fim": today + timedelta(days=18), "capacidade": 30},
            ]),
            ("Carla Mendes", today - timedelta(days=6), 1, [
                {"nome": "couve", "tipo": "hortícola-folha", "biologico": False, "inicio": today, "fim": today + timedelta(days=30), "capacidade": 50},
                {"nome": "acelga", "tipo": "hortícola-folha", "biologico": True, "inicio": today, "fim": today + timedelta(days=20), "capacidade": 20},
                {"nome": "nabiça", "tipo": "hortícola-folha", "biologico": False, "inicio": today, "fim": today + timedelta(days=25), "capacidade": 15},
            ]),
            # Fornecedores de Hortícolas - Fruto (Biológico)
            ("Tiago Ramos", today - timedelta(days=5), 1, [
                {"nome": "tomate", "tipo": "hortícola-fruto", "biologico": True, "inicio": today, "fim": today + timedelta(days=40), "capacidade": 100},
                {"nome": "pimento", "tipo": "hortícola-fruto", "biologico": True, "inicio": today, "fim": today + timedelta(days=45), "capacidade": 35},
                {"nome": "beringela", "tipo": "hortícola-fruto", "biologico": False, "inicio": today, "fim": today + timedelta(days=40), "capacidade": 25},
            ]),
            ("Sofia Almeida", today - timedelta(days=4), 1, [
                {"nome": "tomate cereja", "tipo": "hortícola-fruto", "biologico": True, "inicio": today, "fim": today + timedelta(days=35), "capacidade": 20},
                {"nome": "tomate coração de boi", "tipo": "hortícola-fruto", "biologico": False, "inicio": today, "fim": today + timedelta(days=30), "capacidade": 15},
            ]),
            # Fornecedores de Raízes e Tubérculos
            ("Bruno Ferreira", today - timedelta(days=3), 1, [
                {"nome": "cenoura", "tipo": "tubérculo", "biologico": True, "inicio": today, "fim": today + timedelta(days=120), "capacidade": 80},
                {"nome": "beterraba", "tipo": "tubérculo", "biologico": True, "inicio": today, "fim": today + timedelta(days=120), "capacidade": 50},
                {"nome": "nabo", "tipo": "tubérculo", "biologico": False, "inicio": today, "fim": today + timedelta(days=90), "capacidade": 30},
            ]),
            ("Rita Gomes", today - timedelta(days=3), 1, [
                {"nome": "batata", "tipo": "tubérculo", "biologico": False, "inicio": today, "fim": today + timedelta(days=150), "capacidade": 150},
                {"nome": "abóbora", "tipo": "tubérculo", "biologico": True, "inicio": today, "fim": today + timedelta(days=120), "capacidade": 60},
            ]),
            # Fornecedores de Proteína Animal
            ("Carlos Lopes", today - timedelta(days=5), 1, [
                {"nome": "ovo", "tipo": "proteína", "biologico": True, "inicio": today, "fim": today + timedelta(days=365), "capacidade": 200},
                {"nome": "frango", "tipo": "proteína", "biologico": False, "inicio": today, "fim": today + timedelta(days=365), "capacidade": 150},
            ]),
            ("Fernanda Costa", today - timedelta(days=4), 1, [
                {"nome": "bovino", "tipo": "proteína", "biologico": True, "inicio": today, "fim": today + timedelta(days=365), "capacidade": 100},
                {"nome": "suíno", "tipo": "proteína", "biologico": False, "inicio": today, "fim": today + timedelta(days=365), "capacidade": 80},
                {"nome": "borrego", "tipo": "proteína", "biologico": True, "inicio": today, "fim": today + timedelta(days=365), "capacidade": 60},
            ]),
            ("Gisela Martins", today - timedelta(days=6), 1, [
                {"nome": "pato", "tipo": "proteína", "biologico": False, "inicio": today, "fim": today + timedelta(days=365), "capacidade": 40},
                {"nome": "coelho", "tipo": "proteína", "biologico": True, "inicio": today, "fim": today + timedelta(days=365), "capacidade": 30},
                {"nome": "peru", "tipo": "proteína", "biologico": False, "inicio": today, "fim": today + timedelta(days=365), "capacidade": 20},
            ]),
            # Fornecedores de Especiais
            ("Helena Rocha", today - timedelta(days=7), 1, [
                {"nome": "mel", "tipo": "especial", "biologico": True, "inicio": today, "fim": today + timedelta(days=365), "capacidade": 50},
            ]),
            ("Ivan Ferreira", today - timedelta(days=5), 1, [
                {"nome": "cogumelo shiitake", "tipo": "especial", "biologico": True, "inicio": today, "fim": today + timedelta(days=60), "capacidade": 25},
                {"nome": "cogumelo ostra", "tipo": "especial", "biologico": True, "inicio": today, "fim": today + timedelta(days=60), "capacidade": 20},
            ]),
            ("Joana Alves", today - timedelta(days=6), 1, [
                {"nome": "castanha", "tipo": "especial", "biologico": True, "inicio": today, "fim": today + timedelta(days=120), "capacidade": 40},
            ]),
            # Fornecedores de Especiarias e Aromáticos
            ("Katia Silva", today - timedelta(days=8), 1, [
                {"nome": "alho", "tipo": "condimento", "biologico": True, "inicio": today, "fim": today + timedelta(days=150), "capacidade": 50},
                {"nome": "cebola", "tipo": "condimento", "biologico": False, "inicio": today, "fim": today + timedelta(days=150), "capacidade": 60},
            ]),
            ("Lúcia Mendes", today - timedelta(days=7), 1, [
                {"nome": "salsa", "tipo": "aromático", "biologico": True, "inicio": today, "fim": today + timedelta(days=20), "capacidade": 15},
                {"nome": "cilantro", "tipo": "aromático", "biologico": True, "inicio": today, "fim": today + timedelta(days=20), "capacidade": 12},
                {"nome": "manjericão", "tipo": "aromático", "biologico": False, "inicio": today, "fim": today + timedelta(days=25), "capacidade": 10},
            ]),
            # Fornecedores não aprovados (para teste)
            ("Marcus Oliveira", today - timedelta(days=4), 0, [
                {"nome": "curgete", "tipo": "hortícola-fruto", "biologico": False, "inicio": today, "fim": today + timedelta(days=35), "capacidade": 30},
            ]),
            ("Natália Costa", today - timedelta(days=5), 0, [
                {"nome": "melão", "tipo": "fruta", "biologico": True, "inicio": today, "fim": today + timedelta(days=45), "capacidade": 25},
            ]),
        ]

        for nome, d_insc, aprovado, produtos in samples:
            insert_fornecedor(session, nome, d_insc, aprovado, produtos)

        session.commit()
        print("Inseridos fornecedores de exemplo com sucesso.")
    
    except Exception as e:
        session.rollback()
        print(f"Erro ao inserir dados: {e}")
        raise
    finally:
        session.close()


if __name__ == '__main__':
    main()
