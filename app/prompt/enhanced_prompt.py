# app/prompt/enhanced_prompt.py

from app.fshot.few_shot_selector import get_example_selector
import logging


def check_for_tools(tools: bool) -> bool:
    """
    Retorna si el agente debe usar herramientas.
    """
    return False

def get_fshot_ex_from_question(question: str) -> str:
    """
    Retorna un ejemplo de few shot basado en la pregunta.
    """
    selector = get_example_selector(3)
    examples_str = selector.format_examples_for_prompt(question)
    return examples_str # string formateado. 



def get_enhanced_prompt(question: str, tools: bool) -> str:
    """
    Retorna un prompt mejorado para el agente.
    """
    prompt = f"""
        Eres un analista de datos para Kaana Resorts. Tu funcion es ayudar al usuario a responder preguntas sobre el hotel y sus servicios. 

        Flujo de trabajo:
        1. Analiza cuidadosamente la pregunta del usuario. Decide que herramientas usaras. 
        2. Si decides usar herramientas, selecciona las mas apropiadas para responder la pregunta.
        3. Si no usas herramientas, responde directamente a la pregunta.

            
    """
    
    """ # -> Esto aun no se ha implementado. 
    try:
        examples = get_fshot_ex_from_question(question)
        if examples:
            prompt += "\n" + examples + "\n"
            #logging.info(f"Few shot examples añadidos al prompt.")
            #logging.info(f"Few shot examples: {examples}")
    except Exception as e:
        print(f"Error obteniendo few shot examples: {e}")
    """

    prompt += """

        Recuerda:
        - Nunca inventes informacion. 
        - Puedes devolver una pregunta si crees que te falta informacion para poder responderla. 
        - Invita al usuario a proporcionar mas detalles si es necesario.
        - Al responder la pregunta, invita al usuario a preguntar cualquier otra cosa relacionada con Kaana Resorts.



    """
    
    return prompt