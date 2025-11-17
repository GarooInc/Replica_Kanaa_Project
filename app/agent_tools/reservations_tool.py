# app/agent_tools/reservations_tool.py

from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
import logging

from app.agent_tools.helpers.load_sql_credentials import DATABASE_URL_RESERVATIONS
from app.agent_tools.helpers.custom_table_info import CUSTOM_TABLE_INFO_RESERVATIONS

from app.core.llm_state import LLM

def set_connection():
    try: # Cargar credenciales
        db_res = SQLDatabase.from_uri(
            DATABASE_URL_RESERVATIONS, 
            custom_table_info=CUSTOM_TABLE_INFO_RESERVATIONS,
            sample_rows_in_table_info=3,
            include_tables=list(CUSTOM_TABLE_INFO_RESERVATIONS.keys())
        )
        return db_res
    except Exception as e:
        logging.error(f"Error al conectar a la base de datos de reservas: {e}")
        return None
    
def get_reservations_tool():
    """
    Devuelve una lista de herramientas basadas en la base de datos de reservas.
    Cada herramienta tiene un prefijo 'reservations_' para evitar conflictos de nombres.
    """
    db_res = set_connection()
    toolkit_res = SQLDatabaseToolkit(db=db_res, llm=LLM)
    context_res = toolkit_res.get_context()
    db_tools_res = toolkit_res.get_tools()

    for tool in db_tools_res:
        tool.name = f"res_{tool.name}"

    return db_tools_res