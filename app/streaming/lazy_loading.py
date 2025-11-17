# app/streaming/lazy_loading.py

import logging
from typing import Any, Optional

import app.core.llm_state as llm_state

logger = logging.getLogger(__name__)

_BOUND_LLM: Optional[Any] = None


def bind_tools(tools: list, force_rebind: bool = False):
    """
    Bindea las tools al LLM global solo una vez.
    Usa llm_state.LLM directamente.
    """

    global _BOUND_LLM

    # Primer bind
    if _BOUND_LLM is None:
        _BOUND_LLM = llm_state.LLM.bind_tools(tools)
        llm_state.LLM = _BOUND_LLM
        llm_state.TOOLS = tools
        return _BOUND_LLM

    # Rebind forzado
    if force_rebind:
        _BOUND_LLM = llm_state.LLM.bind_tools(tools)
        llm_state.LLM = _BOUND_LLM
        llm_state.TOOLS = tools
        return _BOUND_LLM

    # Ya existía → retorna el mismo
    return _BOUND_LLM
