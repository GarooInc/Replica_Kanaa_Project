# app/streaming/streaming.py

import logging
import json
from typing import AsyncIterator, List, Dict, Any

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage
)

from app.core.llm_state import LLM
from app.agent_tools.tool_getter import get_agent_tools
from app.streaming.lazy_loading import bind_tools
from app.streaming.tool_execution import execute_tool
from app.utilities.photo_uploader import upload_first_photo_found
from app.prompt.enhanced_prompt import get_enhanced_prompt

from app.streaming.event_handler import (
    send_event,
    send_done,
    send_error
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tools + LLM (idéntico al original)
tools = get_agent_tools()
llm_with_tools = bind_tools(tools, force_rebind=False)
tools_map = {t.name: t for t in tools}


async def ask_streaming(
    question: str,
    message_history: List[Dict] = [],
    max_iterations: int = 8
) -> AsyncIterator[str]:

    try:
        logger.info(f"Starting REAL streaming for question: {question[:60]}")

        if not question.strip():
            async for c in send_event("answer", "Por favor proporciona una pregunta válida."):
                yield c
            async for c in send_done():
                yield c
            return

        prompt = get_enhanced_prompt(question, bool(tools))

        # =======================
        # Historia EXACTA original
        # =======================
        chat_history = [SystemMessage(content=prompt)]

        for msg in message_history:
            if msg.get("role") == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") in ["agent", "assistant"]:
                chat_history.append(AIMessage(content=msg["content"]))

        chat_history.append(HumanMessage(content=question))

        tool_log: List[Dict[str, Any]] = []
        url_image = None

        # ========================
        # LOOP PRINCIPAL ReAct
        # ========================
        for iteration in range(max_iterations):
            logger.info(f"Iteration {iteration+1}/{max_iterations}")

            try:
                # invoke() EXACTO como el agente original
                response = llm_with_tools.invoke(chat_history)
                tool_calls = getattr(response, "tool_calls", None)

                # ========================
                # SIN TOOL CALLS → FINAL
                # ========================
                if not tool_calls:
                    # Buscar imagen opcional
                    try:
                        url_image = upload_first_photo_found()
                    except Exception as e:
                        logger.error(f"Error buscando imágenes: {e}")

                    # STREAMING REAL DEL LLM
                    async for chunk in llm_with_tools.astream(chat_history):
                        if hasattr(chunk, "content") and chunk.content:
                            async for c in send_event("answer", {"content": chunk.content}):
                                yield c

                    if url_image:
                        async for c in send_event("answer", {"content": f"![image]({url_image})"}):
                            yield c

                    if tool_log:
                        async for c in send_event("tool_log", tool_log):
                            yield c

                    async for c in send_done():
                        yield c
                    return

                # ==========================================
                # HAY TOOL CALLS
                # ==========================================
                chat_history.append(response)

                for tool_call in tool_calls:
                    tool_name = tool_call.get("name")
                    tool_args = tool_call.get("args", {})
                    tool_id = tool_call.get("id")

                    # log interno
                    tool_log.append({
                        "iteration": iteration + 1,
                        "tool_name": tool_name,
                        "tool_args": tool_args
                    })

                    # Evento SSE: inicio de herramienta
                    async for c in send_event("tool_usage", f"Iniciando herramienta: {tool_name}"):
                        yield c

                    # Ejecutar herramienta (igual que antes)
                    tool = tools_map.get(tool_name)

                    if tool is None:
                        error_msg = f"Herramienta '{tool_name}' no encontrada"
                        chat_history.append(ToolMessage(content=error_msg, tool_call_id=tool_id))
                        async for c in send_event("tool_usage", error_msg):
                            yield c
                        continue

                    result = await execute_tool(
                        tool,
                        tool_name,
                        tool_args,
                        iteration + 1,
                        tool_log
                    )

                    # agregar resultado a la historia
                    chat_history.append(
                        ToolMessage(content=str(result), tool_call_id=tool_id)
                    )

                    # evento SSE: completado
                    async for c in send_event("tool_usage", f"Completado: {tool_name}"):
                        yield c

            except Exception as err:
                logger.error(f"Error in iteration: {err}")

                async for c in send_event(
                    "answer",
                    {"content": "Ocurrió un error procesando tu consulta."}
                ):
                    yield c

                async for c in send_done():
                    yield c
                return

        # ================================
        # LÍMITE DE ITERACIONES
        # ================================
        final_prompt = chat_history + [
            HumanMessage(content="Proporciona una respuesta final basada en todo lo anterior.")
        ]

        async for chunk in llm_with_tools.astream(final_prompt):
            if hasattr(chunk, "content") and chunk.content:
                async for c in send_event("answer", {"content": chunk.content}):
                    yield c

        if tool_log:
            async for c in send_event("tool_log", tool_log):
                yield c

        async for c in send_done():
            yield c

    except Exception as critical:
        logger.error(f"Critical error: {critical}")

        async for c in send_event(
            "answer",
            {"content": "Error crítico inesperado. Intenta nuevamente."}
        ):
            yield c

        async for c in send_done():
            yield c
