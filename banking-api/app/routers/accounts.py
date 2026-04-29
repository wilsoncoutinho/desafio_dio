import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth import get_current_user
from app.database import get_db
from app.models import Account, User
from app.schemas import AccountOut

router = APIRouter(prefix="/accounts", tags=["Contas Correntes"])


def _generate_account_number() -> str:
    """Generates a unique 10-digit account number."""
    return str(uuid.uuid4().int)[:10]


@router.post(
    "/",
    response_model=AccountOut,
    status_code=status.HTTP_201_CREATED,
    summary="Abrir nova conta corrente",
    description="Cria uma nova conta corrente vinculada ao usuário autenticado. O número da conta é gerado automaticamente.",
)
async def create_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = Account(
        account_number=_generate_account_number(),
        balance=0.0,
        owner_id=current_user.id,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get(
    "/",
    response_model=list[AccountOut],
    summary="Listar minhas contas",
    description="Retorna todas as contas correntes do usuário autenticado.",
)
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Account).where(Account.owner_id == current_user.id)
    )
    return result.scalars().all()


@router.get(
    "/{account_id}",
    response_model=AccountOut,
    summary="Consultar conta por ID",
    description="Retorna os detalhes de uma conta corrente específica. A conta deve pertencer ao usuário autenticado.",
)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.owner_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada.")
    return account
