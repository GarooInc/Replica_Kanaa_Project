# app/agent_tools/tool_getter.py

from app.agent_tools.rag_tool import get_hotel_context_tool
from app.agent_tools.websearch_tool import internet_search
from app.agent_tools.sandbox_tool import python_sandbox_tool
from app.agent_tools.financial_tool import get_financial_tool
from app.agent_tools.reservations_tool import get_reservations_tool
from app.agent_tools.semanticsearch_tool import get_semantic_tool

import logging

# CONFIGURACIÓN DE LOGGING
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def get_agent_tools():
    tools = []
    try:  # hotel context tool
        hotel_tool = get_hotel_context_tool()
        if hotel_tool is not None:
            tools.append(hotel_tool)
            logger.info("hotel_context_search tool añadida a la lista de herramientas.")
    except Exception as e:
        logger.error(f"Error al obtener hotel_context_search tool: {e}")

    try: # internet search tool
        web_tool = internet_search
        if web_tool is not None:
            tools.append(web_tool)
            logger.info("internet_search tool añadida a la lista de herramientas.")
    except Exception as e:
        logger.error(f"Error al obtener internet_search tool: {e}")

    try: # python sandbox tool
        if python_sandbox_tool is not None:
            tools.append(python_sandbox_tool)
            logger.info("python_sandbox tool añadida a la lista de herramientas.")
    except Exception as e:
        logger.error(f"Error al obtener python_sandbox tool: {e}")

    """try: # financial tool
        financial_tools = get_financial_tool()
        if financial_tools:
            tools.extend(financial_tools)
            logger.info("financial tools añadidas a la lista de herramientas.")
    except Exception as e:
        logger.error(f"Error al obtener financial tools: {e}")

    try: # reservations tool
        reservations_tools = get_reservations_tool()
        if reservations_tools:
            tools.extend(reservations_tools)
            logger.info("reservations tools añadidas a la lista de herramientas.")
    except Exception as e:
        logger.error(f"Error al obtener reservations tools: {e}")

    try: # semantic search tool
        semantic_tool = get_semantic_tool()
        if semantic_tool is not None:
            tools.append(semantic_tool)
            logger.info("semantic_search tool añadida a la lista de herramientas.")
    except Exception as e:
        logger.error(f"Error al obtener semantic_search tool: {e}")"""

    tools_map = {tool.name: tool for tool in tools if tool is not None}
    tool_names = ", ".join(tools_map.keys()) if tools_map else "ninguna"
    
    return tools