# enchanced_sandbox.py - Solución con globals correctos

import logging
from langchain_experimental.utilities import PythonREPL
from langchain.tools import Tool
import io
import requests
import random
import string
from datetime import datetime


class FixedPythonREPL(PythonREPL):
    def __init__(self, **kwargs):
        # Preparar globals con todas las funciones e imports necesarios
        custom_globals = {
            # Imports básicos
            '__builtins__': __builtins__,
            'io': io,
            'requests': requests,
            'random': random,
            'string': string,
            'datetime': datetime,
        }
        
        # Importar matplotlib y pandas en globals
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import pandas as pd
            import numpy as np
            
            custom_globals.update({
                'matplotlib': matplotlib,
                'plt': plt,
                'pandas': pd,
                'pd': pd,
                'numpy': np,
                'np': np,
            })
        except ImportError as e:
            print(f"Warning: Could not import some modules: {e}")
        
        # Inicializar PythonREPL con nuestros globals
        super().__init__(_globals=custom_globals, **kwargs)
        logging.info("REPL inicializado con globals personalizados")

def create_fixed_sandbox_tool() -> Tool:
    repl = FixedPythonREPL()
    return Tool(
        name="python_sandbox",
        func=repl.run,
        description=(
            "Ejecuta código Python con matplotlib, pandas, numpy. "
            "Puedes crear y guardar graficos en disco. La imagen embedida en markdown sera mostrada automaticamente si hay una. No intentes mostrarla tu mismo."
        ),
    )

