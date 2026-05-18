import os
from dotenv import load_dotenv

load_dotenv()

print(f"DB_HOST={os.getenv('DB_HOST')}")
print(f"DB_PORT={os.getenv('DB_PORT')}")
print(f"DB_USER={os.getenv('DB_USER')}")
print(f"DB_NAME={os.getenv('DB_NAME')}")

# Check the connection string that would be built
from urllib.parse import quote_plus
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT") or "1433"
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD") or ""
db_name = os.getenv("DB_NAME")

password_encoded = quote_plus(password)
conn_str = f"mssql+pyodbc://{user}:{password_encoded}@{host},{port}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server"
print(f"\nFull connection string (password hidden):")
print(f"mssql+pyodbc://{user}:***@{host},{port}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server")
