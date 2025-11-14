# app/agent_tools/rag_tool.py

from langchain.tools import Tool, BaseTool

# ============== RAG ==============
"""
Inicialización del contexto hotelero (RAG) siguiendo la misma lógica
que semantic_search_find: se carga una sola vez, y las funciones
comprueban que el retriever esté disponible.
"""

from langchain.tools.retriever import create_retriever_tool
from ..rag.rag_store import get_global_retriever
import logging

# Estado interno del módulo
_hotel_context_tool = None
_retriever_ready = False

def _init_hotel_context_tool():
    """Inicializa la herramienta de contexto hotelero si el retriever está disponible."""
    global _hotel_context_tool, _retriever_ready
    try:
        retriever = get_global_retriever()
        if retriever is None:
            logging.warning("⚠️ El retriever global aún no está disponible. Esperando inicialización...")
            return None
        _hotel_context_tool = create_retriever_tool(
            retriever=retriever,
            name="hotel_context_search",
            description=(
                "Busca información sobre Itzana Resorts: servicios, amenidades, políticas, contexto del hotel."
            ),
        )
        _retriever_ready = True
        logging.info("✅ Tool hotel_context_search inicializada correctamente.")
        return _hotel_context_tool
    except Exception as e:
        logging.error(f"❌ Error al inicializar hotel_context_search: {e}")
        _hotel_context_tool = None
        _retriever_ready = False
        return None

def get_hotel_context_tool():
    """Devuelve la tool hotel_context_search, inicializándola si no existe."""
    global _hotel_context_tool, _retriever_ready
    if _hotel_context_tool is None or not _retriever_ready:
        return _init_hotel_context_tool()
    return _hotel_context_tool

# Inicialización automática (una sola vez al importar)
hotel_context_tool = get_hotel_context_tool()
if hotel_context_tool is None:
    logging.warning("La herramienta hotel_context_search no está disponible.")