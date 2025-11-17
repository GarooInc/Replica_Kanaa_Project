# app/agent_tools/sandbox_tool.py
from langchain_experimental.utilities import PythonREPL
from langchain.tools import Tool


# ============== PYTHON SANDBOX ==============
python_repl = PythonREPL()
python_sandbox_tool = Tool(
    name="python_sandbox",
    func=python_repl.run,
    description=(
        "Ejecuta código Python con pandas, matplotlib, numpy. "
        "Permite análisis estadístico y visualizaciones."
        "Si creas graficos, guardalos en el disco. La imagen embedida en markdown sera mostrada automaticamente si hay una. No intentes mostrarla tu mismo."
        "Nunca uses .plt.show(). Unicamente usa plt.savefig('nombre.png') para guardar la imagen."
    ),
)