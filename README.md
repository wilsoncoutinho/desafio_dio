# 🏦 API Bancária Assíncrona — FastAPI + JWT

API RESTful assíncrona para gerenciamento de operações bancárias: depósitos, saques e extrato de conta corrente, com autenticação JWT.

---

## 🚀 Tecnologias

| Tecnologia | Papel |
|---|---|
| **FastAPI** | Framework web assíncrono |
| **SQLAlchemy (async)** | ORM com suporte a `async/await` |
| **aiosqlite** | Driver SQLite assíncrono |
| **python-jose** | Geração e validação de JWT |
| **passlib** | Hash de senha (PBKDF2-SHA256) |
| **Pydantic v2** | Validação de dados e schemas |

---

## 📁 Estrutura do Projeto

```
banking-api/
├── app/
│   ├── main.py          # Aplicação FastAPI + lifespan
│   ├── database.py      # Engine async + sessão
│   ├── models.py        # Modelos SQLAlchemy (User, Account, Transaction)
│   ├── schemas.py       # Schemas Pydantic
│   ├── auth.py          # JWT helpers + dependência get_current_user
│   └── routers/
│       ├── auth.py      # POST /auth/register, POST /auth/login
│       ├── accounts.py  # CRUD de contas correntes
│       └── transactions.py  # Depósito, saque e extrato
└── requirements.txt
```

---

## ⚙️ Instalação

```bash
# Clonar / entrar na pasta
cd banking-api

# Instalar dependências
poetry install

# Iniciar o servidor
poetry run uvicorn app.main:app --reload
```

Acesse **http://localhost:8000/docs** para a documentação interativa (Swagger UI).

---

## 🔑 Autenticação

A API usa **JWT Bearer Token**. Fluxo:

1. Cadastre-se em `POST /auth/register`
2. Faça login em `POST /auth/login` → receba o `access_token`
3. Clique em **Authorize 🔒** no Swagger e cole o token
4. Todos os endpoints de conta e transação exigem o token

---

## 📋 Principais Endpoints

### Autenticação
- `POST /auth/register`: Criar usuário
- `POST /auth/login`: Obter token JWT

### Contas
- `POST /accounts/`: Abrir conta (requer login)
- `GET /accounts/`: Listar minhas contas

### Transações
- `POST /transactions/deposit`: Depositar (requer login)
- `POST /transactions/withdraw`: Sacar (requer login)
- `GET /transactions/statement/{account_id}`: Ver extrato

---

## ✅ Validações
- Saldo insuficiente no saque.
- Valores negativos em transações.
- E-mail único no cadastro.
- Proteção de rotas com JWT.