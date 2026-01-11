"""
Receitas padrão para o catálogo da cantina
Usam APENAS produtos disponíveis nos fornecedores
"""

RECEITAS_CATOLOG = [
    # ==== ALMOÇOS - Disponíveis o ano todo ====
    {
        "nome": "Frango Grelhado com Cenoura",
        "descricao": "Peito de frango grelhado com cenoura cozida",
        "tipo_refeicao": "almoço",
        "categoria": "carne",
        "porcoes_base": 1,
        "tempo_preparo": 35,
        "ingredientes": [
            {"produto": "Frango", "quantidade_por_porcao": 0.15},
            {"produto": "Cenoura", "quantidade_por_porcao": 0.15},
            {"produto": "Ovos", "quantidade_por_porcao": 1},
        ]
    },
    {
        "nome": "Carne de Vaca com Legumes",
        "descricao": "Carne de vaca estufada com cenoura",
        "tipo_refeicao": "almoço",
        "categoria": "carne",
        "porcoes_base": 1,
        "tempo_preparo": 60,
        "ingredientes": [
            {"produto": "Carne de Vaca", "quantidade_por_porcao": 0.15},
            {"produto": "Cenoura", "quantidade_por_porcao": 0.12},
        ]
    },
    {
        "nome": "Peru Assado",
        "descricao": "Peru assado com cenoura",
        "tipo_refeicao": "almoço",
        "categoria": "carne",
        "porcoes_base": 1,
        "tempo_preparo": 50,
        "ingredientes": [
            {"produto": "Peru", "quantidade_por_porcao": 0.15},
            {"produto": "Cenoura", "quantidade_por_porcao": 0.1},
        ]
    },
    {
        "nome": "Peixe Grelhado",
        "descricao": "Peixe grelhado simples",
        "tipo_refeicao": "almoço",
        "categoria": "peixe",
        "porcoes_base": 1,
        "tempo_preparo": 30,
        "ingredientes": [
            {"produto": "Peixe", "quantidade_por_porcao": 0.18},
            {"produto": "Cenoura", "quantidade_por_porcao": 0.1},
        ]
    },
    {
        "nome": "Bacalhau Simples",
        "descricao": "Bacalhau cozido com cenoura",
        "tipo_refeicao": "almoço",
        "categoria": "peixe",
        "porcoes_base": 1,
        "tempo_preparo": 40,
        "ingredientes": [
            {"produto": "Bacalhau", "quantidade_por_porcao": 0.15},
            {"produto": "Cenoura", "quantidade_por_porcao": 0.15},
            {"produto": "Ovos", "quantidade_por_porcao": 1},
        ]
    },
    
    # ==== ALMOÇOS - Primavera/Verão (com tomate, alface) ====
    {
        "nome": "Frango com Salada",
        "descricao": "Frango grelhado com salada fresca",
        "tipo_refeicao": "almoço",
        "categoria": "carne",
        "porcoes_base": 1,
        "tempo_preparo": 30,
        "ingredientes": [
            {"produto": "Frango", "quantidade_por_porcao": 0.15},
            {"produto": "Tomate", "quantidade_por_porcao": 0.1},
            {"produto": "Alface", "quantidade_por_porcao": 0.08},
        ]
    },
    
    # ==== JANTARES - Disponíveis o ano todo ====
    {
        "nome": "Omeleta Simples",
        "descricao": "Omeleta com queijo",
        "tipo_refeicao": "jantar",
        "categoria": "vegetariano",
        "porcoes_base": 1,
        "tempo_preparo": 15,
        "ingredientes": [
            {"produto": "Ovos", "quantidade_por_porcao": 2},
            {"produto": "Queijo", "quantidade_por_porcao": 0.05},
            {"produto": "Leite", "quantidade_por_porcao": 0.05},
        ]
    },
    {
        "nome": "Sopa de Cenoura",
        "descricao": "Sopa cremosa de cenoura",
        "tipo_refeicao": "jantar",
        "categoria": "vegetariano",
        "porcoes_base": 1,
        "tempo_preparo": 30,
        "ingredientes": [
            {"produto": "Cenoura", "quantidade_por_porcao": 0.2},
            {"produto": "Leite", "quantidade_por_porcao": 0.1},
        ]
    },
    
    # ==== JANTARES - Primavera/Verão ====
    {
        "nome": "Salada de Alface e Tomate",
        "descricao": "Salada fresca com queijo",
        "tipo_refeicao": "jantar",
        "categoria": "vegetariano",
        "porcoes_base": 1,
        "tempo_preparo": 15,
        "ingredientes": [
            {"produto": "Alface", "quantidade_por_porcao": 0.15},
            {"produto": "Tomate", "quantidade_por_porcao": 0.12},
            {"produto": "Queijo", "quantidade_por_porcao": 0.05},
        ]
    },
    
    # ==== JANTARES - Outono (com beterraba) ====
    {
        "nome": "Salada de Beterraba",
        "descricao": "Salada morna de beterraba com queijo",
        "tipo_refeicao": "jantar",
        "categoria": "vegetariano",
        "porcoes_base": 1,
        "tempo_preparo": 35,
        "ingredientes": [
            {"produto": "Beterraba", "quantidade_por_porcao": 0.15},
            {"produto": "Cenoura", "quantidade_por_porcao": 0.1},
            {"produto": "Queijo", "quantidade_por_porcao": 0.05},
        ]
    },
]
