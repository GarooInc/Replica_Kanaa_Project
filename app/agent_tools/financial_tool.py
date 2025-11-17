# app/agent_tools/financial_tool.py

from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
import logging

from app.agent_tools.helpers.load_sql_credentials import DATABASE_URL_FINANCIALS
from app.agent_tools.helpers.custom_table_info import CUSTOM_TABLE_INFO_FINANCIALS

from app.core.llm_state import LLM


def set_connection():
    try: # Cargar credenciales
        db_fin = SQLDatabase.from_uri(
            DATABASE_URL_FINANCIALS, 
            custom_table_info=CUSTOM_TABLE_INFO_FINANCIALS,
            sample_rows_in_table_info=3,
            include_tables=list(CUSTOM_TABLE_INFO_FINANCIALS.keys())
        )
        return db_fin
    except Exception as e:
        logging.error(f"Error al conectar a la base de datos financiera: {e}")
        return None
    
def get_financial_tool():
    """
    Devuelve una lista de herramientas basadas en la base de datos financiera.
    Cada herramienta tiene un prefijo 'financials_' para evitar conflictos de nombres.
    """
    db_fin = set_connection()
    toolkit_fin = SQLDatabaseToolkit(db=db_fin, llm=LLM)
    context_fin = toolkit_fin.get_context()
    db_tools_fin = toolkit_fin.get_tools()

    for tool in db_tools_fin:
        tool.name = f"fin_{tool.name}"

    return db_tools_fin

