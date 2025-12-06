from fastapi import FastAPI
from .controllers.fornecedorController import router as fornecedores_router
from .controllers.produtoController import router as produtos_router
from .controllers.authController import router as auth_router

app = FastAPI(title="BioCantinas - Fornecedores")

# Controllers/Routers
app.include_router(fornecedores_router, prefix="")
app.include_router(produtos_router, prefix="")
app.include_router(auth_router, prefix="")