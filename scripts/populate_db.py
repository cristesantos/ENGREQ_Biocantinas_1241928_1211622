import sqlite3
from datetime import date, timedelta

from biocantinas.backend.app import storage


DB_PATH = storage.DB_PATH


def already_populated(conn) -> bool:
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM fornecedores")
    (n,) = c.fetchone()
    return n >= 10


def insert_fornecedor(conn, nome, data_inscricao, aprovado, produtos):
    c = conn.cursor()
    c.execute(
        "INSERT INTO fornecedores (nome, data_inscricao, aprovado) VALUES (?, ?, ?)",
        (nome, data_inscricao, int(bool(aprovado)))
    )
    fid = c.lastrowid
    for p in produtos:
        c.execute(
            "INSERT INTO produtos (fornecedor_id, nome, intervalo_producao_inicio, intervalo_producao_fim, capacidade) VALUES (?, ?, ?, ?, ?)",
            (fid, p['nome'], p['inicio'], p['fim'], int(p.get('capacidade', 0)))
        )


def main():
    # ensure DB/tables exist
    try:
        storage._init_db()
    except Exception:
        # if already initialized or unavailable, ignore
        pass

    conn = sqlite3.connect(DB_PATH)

    if already_populated(conn):
        print("A base já tem >= 10 fornecedores. Nenhuma ação feita.")
        conn.close()
        return

    today = date.today()

    samples = [
        ("João Silva", today - timedelta(days=10), 1, [
            {"nome": "tomate", "inicio": str(today), "fim": str(today + timedelta(days=30)), "capacidade": 50},
            {"nome": "alface", "inicio": str(today), "fim": str(today + timedelta(days=20)), "capacidade": 30},
        ]),
        ("Maria Oliveira", today - timedelta(days=9), 1, [
            {"nome": "tomate", "inicio": str(today), "fim": str(today + timedelta(days=25)), "capacidade": 20},
        ]),
        ("Pedro Santos", today - timedelta(days=9), 1, [
            {"nome": "tomate", "inicio": str(today), "fim": str(today + timedelta(days=25)), "capacidade": 40},
            {"nome": "kiwi", "inicio": str(today), "fim": str(today + timedelta(days=60)), "capacidade": 10},
        ]),
        ("Ana Costa", today - timedelta(days=8), 1, [
            {"nome": "alface", "inicio": str(today), "fim": str(today + timedelta(days=15)), "capacidade": 25},
            {"nome": "mel", "inicio": str(today), "fim": str(today + timedelta(days=365)), "capacidade": 10},
        ]),
        ("Luís Pereira", today - timedelta(days=7), 1, [
            {"nome": "tomate", "inicio": str(today), "fim": str(today + timedelta(days=40)), "capacidade": 15},
            {"nome": "cogumelo shiitake", "inicio": str(today), "fim": str(today + timedelta(days=90)), "capacidade": 5},
        ]),
        ("Carla Mendes", today - timedelta(days=6), 0, [
            {"nome": "kiwi", "inicio": str(today), "fim": str(today + timedelta(days=60)), "capacidade": 60},
        ]),
        ("Tiago Ramos", today - timedelta(days=5), 1, [
            {"nome": "tomate", "inicio": str(today), "fim": str(today + timedelta(days=10)), "capacidade": 5},
        ]),
        ("Sofia Almeida", today - timedelta(days=4), 0, [
            {"nome": "alface", "inicio": str(today), "fim": str(today + timedelta(days=20)), "capacidade": 10},
        ]),
        ("Bruno Ferreira", today - timedelta(days=3), 1, [
            {"nome": "mel", "inicio": str(today), "fim": str(today + timedelta(days=365)), "capacidade": 20},
            {"nome": "tomate", "inicio": str(today), "fim": str(today + timedelta(days=30)), "capacidade": 10},
        ]),
        ("Rita Gomes", today - timedelta(days=3), 1, [
            {"nome": "tomate", "inicio": str(today), "fim": str(today + timedelta(days=30)), "capacidade": 10},
        ]),
    ]

    for nome, d_insc, aprovado, produtos in samples:
        insert_fornecedor(conn, nome, str(d_insc), aprovado, produtos)

    conn.commit()
    conn.close()

    print("Inseridos fornecedores de exemplo com sucesso.")


if __name__ == '__main__':
    main()
