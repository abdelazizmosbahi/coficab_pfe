import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

password = os.getenv("DB_PASSWORD") or ""
print(f"Raw password from .env: {password}")
print(f"Password length: {len(password)}")
print(f"Password repr: {repr(password)}")

password_encoded = quote_plus(password)
print(f"\nEncoded password: {password_encoded}")

# Build and display the connection string
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT") or "1433"
user = os.getenv("DB_USER")
db_name = os.getenv("DB_NAME")

conn_str = f"mssql+pyodbc://{user}:{password_encoded}@{host},{port}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server"
print(f"\nFull connection string:")
print(conn_str)

# Let's also test the connection with more detail
print("\n" + "="*60)
print("Testing connection...")
print("="*60)

try:
    from sqlalchemy import create_engine, text
    engine = create_engine(conn_str, echo=True)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✓ Connection SUCCESSFUL!")
except Exception as e:
    print(f"✗ Connection FAILED!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
