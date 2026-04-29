from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth import get_current_user
from app.database import get_db
from app.models import Account, Transaction, TransactionType, User
from app.schemas import StatementOut, TransactionCreate, TransactionOut

router = APIRouter(prefix="/accounts/{account_id}/transactions", tags=["Transações"])


async def _get_owned_account(
    account_id: int,
    db: AsyncSession,
    current_user: User,
) -> Account:
    """Fetch account, ensuring it belongs to current_user."""
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.owner_id == current_user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada.")
    return account


@router.post(
    "/deposit",
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar depósito",
    description=(
        "Deposita um valor positivo na conta. "
        "Valores negativos ou zero são rejeitados. "
        "Requer autenticação JWT."
    ),
)
async def deposit(
    account_id: int,
    transaction_in: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await _get_owned_account(account_id, db, current_user)

    account.balance += transaction_in.amount
    transaction = Transaction(
        type=TransactionType.deposit,
        amount=transaction_in.amount,
        balance_after=account.balance,
        description=transaction_in.description,
        account_id=account.id,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


@router.post(
    "/withdrawal",
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar saque",
    description=(
        "Saca um valor positivo da conta. "
        "Retorna 422 se o valor for negativo/zero e 400 se o saldo for insuficiente. "
        "Requer autenticação JWT."
    ),
)
async def withdrawal(
    account_id: int,
    transaction_in: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await _get_owned_account(account_id, db, current_user)

    if transaction_in.amount > account.balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente. Saldo atual: R$ {account.balance:.2f}.",
        )

    account.balance -= transaction_in.amount
    transaction = Transaction(
        type=TransactionType.withdrawal,
        amount=transaction_in.amount,
        balance_after=account.balance,
        description=transaction_in.description,
        account_id=account.id,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


@router.get(
    "/statement",
    response_model=StatementOut,
    summary="Exibir extrato da conta",
    description=(
        "Retorna o extrato completo da conta com todas as transações em ordem cronológica, "
        "o número da conta e o saldo atual. Requer autenticação JWT."
    ),
)
async def get_statement(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await _get_owned_account(account_id, db, current_user)

    result = await db.execute(
        select(Transaction)
        .where(Transaction.account_id == account.id)
        .order_by(Transaction.created_at.asc())
    )
    transactions = result.scalars().all()

    return StatementOut(
        account_number=account.account_number,
        current_balance=account.balance,
        transactions=transactions,
    )
