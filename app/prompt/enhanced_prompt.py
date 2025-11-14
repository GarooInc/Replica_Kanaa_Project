# app/prompt/enhanced_prompt.py


def check_for_tools() -> bool:
    """
    Retorna si el agente debe usar herramientas.
    """
    return False

def check_for_fshotexamples() -> bool:
    """
    Retorna si el agente debe usar few-shot examples.
    """
    return False


def get_enhanced_prompt() -> str:
    """
    Retorna un prompt mejorado para el agente.
    """
    prompt = f"""

    Eres un asistente inteligente diseñado para responder preguntas de usuarios de manera precisa. 
    Trabajas para Kaana Resorts, una luxury resort de Belice famosa por su belleza natural y servicios exclusivos.

    """

    if check_for_tools():
        prompt += f"""
        Descripcion de las herramientas disponibles:
        - 
        """

    if check_for_fshotexamples():
        prompt += f"""
        Ejemplos de preguntas y respuestas:
        - 
        """

    prompt += f"""
    IMPORTANTE:
    - Responde en un formato markdown. 
    - Nunca incluyas codigo o formulas en tu respuesta. 
    - No inventes informacion, si no sabes la respuesta, di que no lo sabes o devuelve una pregunta para etender mejor la consulta.
    - Responde en el mismo idioma en que se te pregunto.
    - Termina con un saludo cordial y una invitacion a preguntar cualquier otra cosa.
    """
    

    return prompt