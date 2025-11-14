# app/agent_tools/websearch_tool.py

from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde el archivo .env

# ============== WEB SEARCH ==============
internet_search = TavilySearch()
internet_search.name = "strategic_web_search"
internet_search.description = (
    "Busca información externa, benchmarks, tendencias del sector hotelero, mejores prácticas."
)

class TavilySearchInput(BaseModel):
    query: str = Field(description="Query para investigación estratégica")

# Actualizar el uso de Pydantic para evitar advertencias
internet_search.args_schema = TavilySearchInput.model_json_schema()