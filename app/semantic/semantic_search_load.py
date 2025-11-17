# semantic_search_load.py
"""
Construye el índice FAISS de cuentas contables usando Cohere embeddings.
Versión simplificada: conexión directa a PostgreSQL sin LangChain.
"""

import os, logging, shutil
from sqlalchemy import create_engine, text
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

# ================= CONFIG =================
load_dotenv()
logging.basicConfig(level=logging.INFO)

PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT", 5432)
PG_NAME = os.getenv("PG_DATABASE")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_NAME}"

BASE_DIR = os.path.join(os.path.dirname(__file__), "../data/semantic_search_faiss_index")
INDEX_NAME = "account_index"
INDEX_PATH = os.path.join(BASE_DIR, INDEX_NAME)

# ================= EMBEDDINGS =================
embedding_model = CohereEmbeddings(
    model="embed-multilingual-light-v3.0",
    cohere_api_key=COHERE_API_KEY
)

# ================= FUNCIONES =================
def get_account_names() -> list[str]:
    """Obtiene nombres de cuenta directamente desde PostgreSQL."""
    logging.info("Conectando a la base de datos...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT DISTINCT account_name FROM dim_accounts WHERE account_name IS NOT NULL;")
        )
        names = [row[0] for row in result if row[0]]
    logging.info(f" {len(names)} nombres recuperados desde la base de datos.")
    print("Ejemplo de cuentas:", names[:10])
    return names

def build_index():
    """Crea el índice FAISS y lo guarda localmente."""
    names = get_account_names()
    print(f"Primeras cuentas encontradas y que se cargarán: {names[:10]}")
    if not names:
        raise ValueError("No se encontraron cuentas válidas en la base de datos.")

    # Crear documentos simples
    docs = [Document(page_content=n, metadata={"account_name": n}) for n in names]

    # Limpiar índice previo
    shutil.rmtree(INDEX_PATH, ignore_errors=True)
    os.makedirs(INDEX_PATH, exist_ok=True)

    # Crear vectorstore
    vectorstore = FAISS.from_documents(docs, embedding_model)
    vectorstore.save_local(INDEX_PATH)
    logging.info(f"Índice FAISS guardado en {INDEX_PATH}. Total: {len(names)} cuentas.")

# ================= MAIN =================
if __name__ == "__main__":
    logging.info("Generando índice FAISS de cuentas...")
    build_index()
    logging.info(" Proceso completado.")

    print(f"\nBase Dir: {BASE_DIR}, \nÍndice: {INDEX_PATH}\n")
