# app/agent_tools/semanticsearch_tool.py

import logging
from pydantic import BaseModel, Field
from langchain.tools import Tool

from app.semantic.semantic_search_find import semantic_search


class AccountSearchInput(BaseModel):
    query: str = Field(description="Término o palabra clave de la cuenta a buscar")

def account_search_tool(input):
    """Permite manejar tanto objetos Pydantic como strings simples"""
    try:
        query = getattr(input, "query", input)  # Si es objeto, toma .query; si es string, usa directo
        results = semantic_search(query, k=5)
        return [r["account_name"] for r in results] if results else []
    except Exception as e:
        logging.error(f"Error en account_search_tool: {e}")
        return []

def get_semantic_tool():
    """Devuelve la herramienta de búsqueda semántica de cuentas."""
    account_search = Tool(
        name="account_search",
        func=account_search_tool,
        description=(
            "Busca nombres de cuentas contables similares usando búsqueda semántica FAISS + Cohere. "
            "Úsala cuando el usuario mencione un término de cuenta financiera y necesites el nombre exacto. "
            "Devuelve hasta 5 coincidencias relevantes."
        ),
        args_schema=AccountSearchInput
    )

    return account_search