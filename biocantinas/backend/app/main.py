from fastapi import FastAPI
from .controllers.fornecedorController import router as fornecedores_router
from .controllers.produtoCatalogoController import router as produtos_catalogo_router
from .controllers.authController import router as auth_router
from .controllers.ementaController import router as ementas_router
from .controllers.aprovisionamentoController import router as aprovisionamento_router
from .controllers.execucaoRefeicaoController import router as execucoes_router
from .controllers.kpiController import router as kpi_router
from .controllers.receitaController import router as receitas_router
from .controllers.relatorioController import router as relatorio_router

app = FastAPI(title="BioCantinas - Fornecedores")

@app.get("/")
def root():
	return {"status": "ok", "message": "BioCantinas API", "docs": "/docs", "openapi": "/openapi.json"}

# Controllers/Routers
app.include_router(fornecedores_router, prefix="")
app.include_router(produtos_catalogo_router, prefix="")
app.include_router(auth_router, prefix="")
app.include_router(ementas_router, prefix="")
app.include_router(aprovisionamento_router, prefix="")
app.include_router(execucoes_router, prefix="")
app.include_router(kpi_router, prefix="")
app.include_router(receitas_router, prefix="")
app.include_router(relatorio_router, prefix="")
