# 📋 SCRIPTS DE SETUP E TESTES - BIOCANTINAS

## 📌 Resumo

Este diretório contém os scripts de inicialização e testes da aplicação BioCantinas. Todos os dados de teste estão consolidados em **um único ficheiro**.

## 🚀 Como Usar

### 1️⃣ **Recriar Base de Dados (Obrigatório primeiro)**

```bash
python scripts/recreate_full_db.py
```

**O que faz:**
- ✅ Deleta a base de dados existente
- ✅ Cria todas as tabelas
- ✅ Popula com dados base (15 utilizadores, 11 fornecedores, 10 receitas, etc.)
- ✅ Cria 4 ementas com 40 refeições baseadas em receitas
- ✅ Cria 4372 reservas de teste
- ✅ Cria 14 execuções de refeições
- ✅ Cria dados históricos para KPIs

### 2️⃣ **Setup Consolidado de Dados para Testes**

```bash
python scripts/setup_dados_testes.py
```

**O que faz:**
- ✅ Limpa ementas antigas
- ✅ Cria 1 ementa para a semana de 05-09 Jan 2026 (Segunda a Sexta)
- ✅ Cria 10 refeições baseadas em receitas do catálogo
- ✅ Cria 15 planos de produção
- ✅ Cria 20 execuções de teste para 10 Jan 2026

**Dados de Teste:**
- Ementa: Segunda 05/01 a Sexta 09/01/2026
- Execuções: Sábado 10/01/2026
- Alunos: 2 (aluno1, aluno2)
- Planos: Frango, Carne, Peixe, Peru, Ovos, Legumes, etc.

---

## 📂 Scripts Detalhados

| Script | Finalidade | Usar | Notas |
|--------|-----------|------|-------|
| `recreate_full_db.py` | Recriar BD completa | ✅ Sempre primeiro | Exclui dados antigos |
| `setup_dados_testes.py` | **Único setup de testes** | ✅ Para testes | Consolidado em um ficheiro |

---

## 🧪 Como Testar o Relatório (Plano vs Realizado)

### Após executar `setup_dados_testes.py`:

1. **Inicie o backend e frontend:**
   ```bash
   # Terminal 1: Backend
   cd biocantinas/backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2: Frontend
   cd biocantinas
   streamlit run frontend/app.py
   ```

2. **Navegue no Streamlit:**
   - Aceda a: `http://localhost:8501`
   - Login: `gestor` / `1`
   - Navegue para: **Gestão da Cantina** → **aba 6: "📈 Comparação Realizado vs Previsto"**

3. **Teste o relatório:**
   - **Data início:** `2026-01-05`
   - **Data fim:** `2026-01-10`
   - Clique em **"📊 Gerar Relatório"**
   - Verá dados de execução vs plano com desvios calculados

4. **Atualize o plano:**
   - Clique em **"💾 Atualizar Plano com Consumo Real"**
   - O sistema calcula consumo real e atualiza `quantidade_realizada`

---

## 📊 Estrutura de Dados de Teste

### Ementas
```
Semana 05-09 Jan 2026
├── Segunda (1):
│   ├── Almoço: Frango Grelhado com Cenoura (100 porções)
│   └── Jantar: Frango com Salada (100 porções)
├── Terça (2):
│   ├── Almoço: Carne de Vaca com Legumes
│   └── Jantar: Omeleta Simples
├── Quarta (3):
│   ├── Almoço: Peru Assado
│   └── Jantar: Sopa de Cenoura
├── Quinta (4):
│   ├── Almoço: Peixe Grelhado
│   └── Jantar: Salada de Alface e Tomate
└── Sexta (5):
    ├── Almoço: Bacalhau Simples
    └── Jantar: Salada de Beterraba
```

### Planos de Produção
| Produto | Quantidade Prevista |
|---------|-------------------|
| Frango | 25 |
| Carne de Vaca | 20 |
| Peixe Grelhado | 15 |
| Bacalhau Simples | 15 |
| Peru | 12 |
| Ovos | 250 |
| Cenoura | 60 |
| Batata | 90 |
| ... | ... |

### Execuções
- **Data:** 10/01/2026 (Sábado)
- **Refeições:** 10 (2 por dia de segunda a sexta)
- **Por refeição:** Produzidas 100, Servidas 90, Não Servidas 10

---

## 🔑 Credenciais de Teste

```
Gestor Cantina:
  Username: gestor
  Password: 1

Dietista:
  Username: dietista
  Password: 1

Aluno 1:
  Username: aluno1
  Password: 1

Aluno 2:
  Username: aluno2
  Password: 1

Produtor 1:
  Username: João Silva
  Password: 1

Produtor 2:
  Username: Maria Carvalho
  Password: 1
```

---

## 🛠️ Manutenção

### Para resetar tudo:
```bash
# 1. Recriar DB
python scripts/recreate_full_db.py

# 2. Setup dados de teste
python scripts/setup_dados_testes.py

# 3. Reiniciar backend
# Ctrl+C no terminal do uvicorn, depois reinicie
```

---

## 📝 Notas

- As **ementas são geradas dinamicamente** a partir das receitas do catálogo
- Os **planos de produção** usam produtos reais do sistema
- As **execuções** simulam refeições realmente feitas (100 produzidas, 90 servidas, 10 desperdício)
- O **relatório de comparação** calcula automáticamente o consumo real vs previsto

---

**Última atualização:** 11 Janeiro 2026
**Versão:** 2.0 (Consolidado)
