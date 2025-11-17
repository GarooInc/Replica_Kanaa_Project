# app/agent_tools/helpers/load_sql_credentials.py

from dotenv import load_dotenv
import os
load_dotenv()

# Leer credenciales desde variables de entorno
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')  # Puerto por defecto de PostgreSQL
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
PG_NAME = os.getenv('PG_DATABASE')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Remover http:// o https:// del host si está presente
if DB_HOST:
    DB_HOST = DB_HOST.replace('http://', '').replace('https://', '').strip()

# Formato: postgresql+psycopg2://user:password@host:port/database
DATABASE_URL_RESERVATIONS = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URL_FINANCIALS = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{PG_NAME}"

def get_res_credentials():
    return {
        "url": DATABASE_URL_RESERVATIONS,
        "host": DB_HOST,
        "port": DB_PORT,
        "database": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD
    }

def get_fin_credentials():
    return {
        "url": DATABASE_URL_FINANCIALS,
        "host": DB_HOST,
        "port": DB_PORT,
        "database": PG_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD
    }