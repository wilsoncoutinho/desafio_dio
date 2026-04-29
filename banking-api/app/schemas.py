from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, field_validator
from app.models import TransactionType


# ── Auth ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ── Account ───────────────────────────────────────────────────────────────────

class AccountCreate(BaseModel):
    """No input needed — account number is auto-generated."""
    pass


class AccountOut(BaseModel):
    id: int
    account_number: str
    balance: float
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Transaction ───────────────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    amount: float
    description: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("O valor da transação deve ser positivo.")
        return v


class TransactionOut(BaseModel):
    id: int
    type: TransactionType
    amount: float
    balance_after: float
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Statement ─────────────────────────────────────────────────────────────────

class StatementOut(BaseModel):
    account_number: str
    current_balance: float
    transactions: List[TransactionOut]

    model_config = {"from_attributes": True}
