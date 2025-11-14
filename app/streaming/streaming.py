# app/streaming/streaming.py

import asyncio
import logging
from typing import AsyncIterator, List, Dict, Any

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage
)

from app.streaming.event_handler import (
    send_event,
    send_done,
    send_error
)

from app.streaming.tool_execution import execute_tool

from app.utilities.photo_uploader import upload_first_photo_found


# CONFIGURACIÓN DE LOGGING
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# FUNCIÓN PRINCIPAL DE STREAMING
async def ask_streaming(
    question: str,
    message_history: List[Dict] = [],
    max_iterations: int = 8,
    tools: List[Any] = [],
    enhanced_prompt: str = "", # deberiamos reemplazarlo por una funcion getter más adelante. 
    base_llm: Any = None
) -> AsyncIterator[str]:
    """
    Streaming con flujo ReAct corregido:
    - Si no hay tool calls → respuesta final y return
    - Si hay error → mensaje humano y return
    - Si llega a max_iterations → respuesta final y return
    - Usa tools basadas únicamente en `tools` list
    """

    try:
        logger.info(f"Starting streaming function for question: {question}")
        
        # VALIDACIÓN BÁSICA
        if not question or not question.strip():
            async for c in send_event("answer", "Por favor, ingresa una pregunta válida."):
                yield c
            async for c in send_done():
                yield c
            return

        
        # CONSTRUIR HISTORIAL
        history = [SystemMessage(content=enhanced_prompt)]

        for msg in message_history:
            if msg.get("role") == "user":
                history.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") in ["agent", "assistant"]:
                history.append(AIMessage(content=msg.get("content", "")))


        history.append(HumanMessage(content=question))
        
        # BIND DEL MODELO Y TOOLS
        llm = base_llm.bind_tools(tools)

        # Lista para registrar uso de herramientas
        tool_log: List[Dict[str, Any]] = []

        # LOOP PRINCIPAL ReAct
        for iteration in range(max_iterations): # default 8
            logger.info(f"Iteration {iteration+1}/{max_iterations}")

            try:
                # Obtener respuesta del modelo
                res = llm.invoke(history)
                tool_calls = getattr(res, "tool_calls", None)

                
                # SIN TOOL CALLS → RESPUESTA FINAL
                if not tool_calls:

                    # check for images
                    try:
                        url_image = upload_first_photo_found()
                        # Incluir URL de imagen si existe
                        url_markdown_format = f"\n![image]({url_image})" if url_image else None
                    except Exception as e:
                        logger.error(f"Error en manejo de imágenes: {e}")

                    # Streaming real de la respuesta final
                    async for chunk in llm.astream(history):
                        if hasattr(chunk, "content") and chunk.content:
                            async for c in send_event("answer", {"content": chunk.content}):
                                yield c

                    if url_markdown_format: # append photo as additional message
                        async for c in send_event("answer", {"content": url_markdown_format}):
                            yield c

                    # Enviar tool log si existe
                    if tool_log:
                        async for c in send_event("tool_log", tool_log):
                            yield c

                    # Finalizar flujo
                    async for c in send_done(): # closes stream and connection
                        yield c
                    return

                
                # HAY TOOL CALLS
                history.append(res)

                for tool_call in tool_calls:
                    tool_name = tool_call.get("name")
                    tool_args = tool_call.get("args", {})
                    tool_id = tool_call.get("id")

                    # Buscar herramienta por nombre
                    selected_tool = next(
                        (t for t in tools if t.name == tool_name),
                        None
                    )

                    
                    # Si herramienta no existe
                    if selected_tool is None:
                        msg = f"Herramienta '{tool_name}' no encontrada."
                        history.append(ToolMessage(content=msg, tool_call_id=tool_id))

                        async for c in send_event("tool_usage", msg):
                            yield c
                        continue

                    
                    # Ejecutar la herramienta (wrapper)
                    result = await execute_tool(
                        selected_tool,
                        tool_name,
                        tool_args,
                        iteration + 1,
                        tool_log
                    )

                    # Agregar resultado al historial
                    history.append(
                        ToolMessage(content=str(result), tool_call_id=tool_id)
                    )

                    # Notificar finalización
                    async for c in send_event("tool_usage", f"Completado: {tool_name}"):
                        yield c

            
            # ERROR EN ITERACIÓN → MENSAJE HUMANO Y RETURN
            except Exception as iteration_error:
                logger.error(f"Error in iteration {iteration+1}: {iteration_error}")

                async for c in send_event(
                    "answer",
                    {"content": "Ha ocurrido un error al procesar tu consulta. Por favor intenta de nuevo."}
                ):
                    yield c

                async for c in send_done():
                    yield c
                return

        
        # ALCANZÓ MÁX IMAGEN ITERACIONES → FORZAR RESPUESTA FINAL
        logger.warning("Max iterations reached.")

        final_prompt = history + [
            HumanMessage(content="Por favor proporciona una respuesta final basada en toda la información disponible.")
        ]

        async for chunk in llm.astream(final_prompt):
            if hasattr(chunk, "content") and chunk.content:
                async for c in send_event("answer", {"content": chunk.content}):
                    yield c

        if tool_log:
            async for c in send_event("tool_log", tool_log):
                yield c

        async for c in send_done():
            yield c
        return

    
    # ERROR GLOBAL → MENSAJE HUMANO
    except Exception as e:
        logger.error(f"Critical error: {e}")

        async for c in send_event(
            "answer",
            {"content": "Ha ocurrido un error inesperado. Por favor intenta nuevamente."}
        ):
            yield c

        async for c in send_done():
            yield c

        return
