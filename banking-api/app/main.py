from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import accounts, auth, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="API Bancária Assíncrona",
    description=(
        "API RESTful assíncrona para gerenciamento de operações bancárias. "
        "Permite cadastro de usuários, abertura de contas correntes, "
        "realização de depósitos e saques, e consulta de extrato. "
        "\n\n**Autenticação:** Use `/auth/login` para obter um token JWT e "
        "clique em **Authorize** (🔒) para autenticar os endpoints protegidos."
    ),
    version="1.0.0",
    contact={"name": "Banking API", "email": "contato@bankingapi.com"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)


@app.get("/", tags=["Health"], summary="Health check")
async def root():
    return {"status": "ok", "message": "API Bancária está no ar 🏦"}
