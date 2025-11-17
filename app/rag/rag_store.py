# app/rag/rag_store.py

"""
rag_store.py
----------------------------------
Gestiona el índice FAISS y expone un retriever global accesible
desde cualquier parte del proyecto (por ejemplo, streaming_agent.py)
"""

from pathlib import Path
import json
import logging
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings
from langchain.tools.retriever import create_retriever_tool
from dotenv import load_dotenv
load_dotenv()  # Carga variables de entorno desde .env si existe

# Configuración
INDEX_DIR = Path(__file__).parent.parent / "data/hotel_context_faiss_index" # se supone que esta bien
CHUNK_STORE_PATH = INDEX_DIR / "chunk_store.json"
EMBED_MODEL = "embed-multilingual-light-v3.0"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# === Retriever global ===
_hotel_retriever = None


def set_global_retriever(retriever):
    """Guarda el retriever globalmente (se usa al iniciar o tras reindexar)."""
    global _hotel_retriever
    _hotel_retriever = retriever
    try:
        from app.agent_tools.rag_tool import get_hotel_context_tool #ATTENTION
        get_hotel_context_tool()  # fuerza creación de tool si aún no existe
    except Exception as e:
        logger.debug(f"No se pudo inicializar hotel_context_tool desde rag_store: {e}")

    


def get_global_retriever():
    """Devuelve el retriever global actual."""
    global _hotel_retriever
    # Inicialización automática del retriever global
    if _hotel_retriever is None:
        try:
            _hotel_retriever = load_vectorstore().as_retriever(k=3)
            logger.info("SUCCESS: Retriever global inicializado.")
        except Exception as e:
            logger.error(f"❌ Error al inicializar el retriever global: {e}")
    return _hotel_retriever


# === Carga básica del vectorstore ===
def load_vectorstore():
    if not INDEX_DIR.exists():
        raise FileNotFoundError(f"FAISS index not found at {INDEX_DIR}")
    embeddings = CohereEmbeddings(model=EMBED_MODEL)
    logger.info("SUCCESS FAISS index cargado correctamente.")
    return FAISS.load_local(
        str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True
    )


def get_retriever(k: int = 3):
    """Crea un nuevo retriever a partir del vectorstore."""
    vs = load_vectorstore()
    return vs.as_retriever(search_kwargs={"k": k})


def initialize_hotel_context_tool():
    """Inicializa la herramienta hotel_context_search de manera explícita."""
    global _hotel_retriever
    try:
        if _hotel_retriever is None:
            _hotel_retriever = load_vectorstore().as_retriever(k=3)
        tool = create_retriever_tool(
            retriever=_hotel_retriever,
            name="hotel_context_search",
            description=(
                "Busca información sobre Itzana Resorts: servicios, amenidades, políticas, contexto del hotel."
            ),
        )
        logger.info("SUCCESS Tool hotel_context_search inicializada correctamente.")
        return tool
    except Exception as e:
        logger.error(f"ERROR al inicializar hotel_context_search: {e}")
        return None

