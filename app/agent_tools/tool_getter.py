# app/agent_tools/tool_getter.py

from app.agent_tools.rag_tool import get_hotel_context_tool
from app.agent_tools.websearch_tool import internet_search

import logging

# CONFIGURACIÓN DE LOGGING
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def get_agent_tools():
    tools = []
    try:   
        hotel_tool = get_hotel_context_tool()
        if hotel_tool is not None:
            tools.append(hotel_tool)
            logger.info("hotel_context_search tool añadida a la lista de herramientas.")
    except Exception as e:
        logger.error(f"Error al obtener hotel_context_search tool: {e}")

    try:
        web_tool = internet_search
        if web_tool is not None:
            tools.append(web_tool)
            logger.info("internet_search tool añadida a la lista de herramientas.")
    except Exception as e:
        logger.error(f"Error al obtener internet_search tool: {e}")
    
    return tools