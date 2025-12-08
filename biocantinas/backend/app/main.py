from fastapi import FastAPI
from .controllers.fornecedorController import router as fornecedores_router
from .controllers.produtoController import router as produtos_router
from .controllers.authController import router as auth_router

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
