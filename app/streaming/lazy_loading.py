# app/streaming/lazy_loading.py

from langchain_openai import ChatOpenAI
from typing import Any, Optional
import logging
from dotenv import load_dotenv
load_dotenv()  # Carga variables de entorno desde .env si existe

llm = ChatOpenAI(
    model ="gpt-4o",
    temperature=0.5,
    streaming=True,
    max_retries=3
)

# Caché para evitar enlazar herramientas más de una vez
_BOUND_LLM: Optional[Any] = None
_BOUND_TOOLS_FINGERPRINT: Optional[tuple] = None

logger = logging.getLogger(__name__)


def bind_tools(tools: list, force_rebind: bool = False) -> ChatOpenAI:
    """
    Vincula herramientas al LLM sólo la primera vez y reutiliza la instancia.

    Parámetros:
    - tools: lista de herramientas a vincular en el primer (o forzado) enlazado.
    - force_rebind: si es True, vuelve a enlazar con las herramientas proporcionadas.
    
    Comportamiento:
    - Primera llamada: enlaza con `tools` y guarda huella.
    - Llamadas posteriores: reutiliza la instancia; si cambian las herramientas, registra warning.
    - Si `force_rebind=True`: vuelve a enlazar y actualiza la huella.
    """
    global _BOUND_LLM, _BOUND_TOOLS_FINGERPRINT
    fp = tuple(getattr(t, 'name', getattr(t, '__name__', repr(t))) for t in (tools or []))

    if _BOUND_LLM is None:
        _BOUND_LLM = llm.bind_tools(tools)
        _BOUND_TOOLS_FINGERPRINT = fp
        return _BOUND_LLM

    if force_rebind:
        _BOUND_LLM = llm.bind_tools(tools)
        _BOUND_TOOLS_FINGERPRINT = fp
        return _BOUND_LLM

    if _BOUND_TOOLS_FINGERPRINT is not None and _BOUND_TOOLS_FINGERPRINT != fp:
        logger.warning(
            "bind_tools() ya fue ejecutado antes; se ignoran nuevas herramientas. Previas=%s, Nuevas=%s",
            _BOUND_TOOLS_FINGERPRINT,
            fp,
        )
    return _BOUND_LLM
