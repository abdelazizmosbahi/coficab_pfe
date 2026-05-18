# db_connection.py
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

def _build_db_url():
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT") or "1433"
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD") or ""
    db_name = os.getenv("DB_NAME")

    missing = [name for name, value in {
        "DB_HOST": host,
        "DB_PORT": port,
        "DB_USER": user,
        "DB_NAME": db_name,
    }.items() if not value]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    password_encoded = quote_plus(password)
    # MSSQL connection uses comma between host and port, not colon
    # TrustServerCertificate=yes allows connection to servers with self-signed or untrusted certificates
    return f"mssql+pyodbc://{user}:{password_encoded}@{host},{port}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
def get_db_engine():
    try:
        engine = create_engine(
            _build_db_url(),
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        )
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return engine
    except (SQLAlchemyError, ValueError) as exc:
        print("\nConnection FAILED!")
        print(f"Error: {exc}")
        return None

def get_db_connection():
    return get_db_engine()

# ────────────────────────────────────────────────
#   Run the test when file is executed directly
# ────────────────────────────────────────────────
if __name__ == "__main__":
    engine = get_db_engine()
    if engine is not None:
        print("→ Test passed: engine is active")
        engine.dispose()
        print("Engine disposed")
    else:
        print("→ Test failed")