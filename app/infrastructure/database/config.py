# =============================================================================
# PostgreSQL Connection
# =============================================================================

POSTGRES_USER = "lokeshkr"
POSTGRES_PASSWORD = "password123"
POSTGRES_SERVER = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "unitybankx"
DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
