# app/streaming/tool_execution.py

async def execute_tool(tool, tool_name, tool_args, iteration, tool_log):
    """
    Ejecuta una herramienta LangChain (async o sync) y registra su uso en tool_log,
    siguiendo el modelo del código 1.
    """

    # Registrar inicio de uso de la herramienta
    tool_log.append({
        "iteration": iteration,
        "tool_name": tool_name,
        "tool_args": tool_args,
        "status": "started"
    })

    try:
        # ==========================
        # Ejecución async
        # ==========================
        if hasattr(tool, "ainvoke"):
            result = await tool.ainvoke(tool_args)

        # ==========================
        # Ejecución sync
        # ==========================
        elif hasattr(tool, "run"):
            # tool.run puede aceptar cadenas, un valor o kwargs
            if len(tool_args) == 0:
                result = tool.run("")
            elif len(tool_args) == 1:
                result = tool.run(list(tool_args.values())[0])
            else:
                result = tool.run(**tool_args)

        # ==========================
        # Sin método conocido
        # ==========================
        else:
            result = f"Tool '{tool_name}' no tiene un método ejecutable."

        # Registrar éxito
        tool_log.append({
            "iteration": iteration,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "status": "completed"
        })

        return result

    except Exception as err:
        # Registrar error
        tool_log.append({
            "iteration": iteration,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "status": "error",
            "error": str(err)
        })

        return f"Error ejecutando '{tool_name}': {err}"
