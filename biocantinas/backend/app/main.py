from fastapi import FastAPI
from .controllers.fornecedorController import router as fornecedores_router
from .controllers.produtoController import router as produtos_router
from .controllers.authController import router as auth_router
from .controllers.ementaController import router as ementas_router
from .controllers.aprovisionamentoController import router as aprovisionamento_router
from .controllers.execucaoRefeicaoController import router as execucoes_router
from .controllers.kpiController import router as kpi_router

app = FastAPI(title="BioCantinas - Fornecedores")


@app.get("/")
def root():
	return {"status": "ok", "message": "BioCantinas API", "docs": "/docs", "openapi": "/openapi.json"}


@app.get("/health")
def health():
	return {"status": "ok"}

# Controllers/Routers
app.include_router(fornecedores_router, prefix="")
app.include_router(produtos_router, prefix="")
app.include_router(auth_router, prefix="")
app.include_router(ementas_router, prefix="")
app.include_router(aprovisionamento_router, prefix="")
app.include_router(execucoes_router, prefix="")
app.include_router(kpi_router, prefix="")
