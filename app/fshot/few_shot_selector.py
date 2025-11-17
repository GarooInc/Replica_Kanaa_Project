# few_shot_selector.py
"""
Selector semántico de ejemplos few-shot para SQL queries
Encuentra los ejemplos más relevantes basándose en similitud de la pregunta
"""

from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from app.fshot.sql_examples import SQL_EXAMPLES

from dotenv import load_dotenv
load_dotenv()

class SQLExampleSelector:
    """Selector de ejemplos SQL basado en similitud semántica"""
    
    def __init__(self, examples=None, k=3):
        """
        Args:
            examples: Lista de ejemplos {input, query}. Si es None, usa SQL_EXAMPLES
            k: Número de ejemplos a seleccionar
        """
        self.examples = examples or SQL_EXAMPLES
        self.k = k
        self.embeddings = CohereEmbeddings(model="large")
        
        # Crear el selector semántico
        self.selector = SemanticSimilarityExampleSelector.from_examples(
            self.examples,
            self.embeddings,
            FAISS,
            k=self.k,
            input_keys=["input"]  # Campo que se usa para la similitud
        )
    
    def select_examples(self, question: str):
        """
        Selecciona los k ejemplos más similares a la pregunta
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Lista de ejemplos relevantes
        """
        return self.selector.select_examples({"input": question})
    
    def format_examples_for_prompt(self, question: str) -> str:
        """
        Formatea los ejemplos seleccionados para incluir en el prompt
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            String formateado con los ejemplos
        """
        examples = self.select_examples(question)
        
        if not examples:
            return ""
        
        formatted = "EJEMPLOS DE QUERIES SIMILARES:\n\n"
        for i, ex in enumerate(examples, 1):
            formatted += f"Ejemplo {i}:\n"
            formatted += f"Pregunta: {ex['input']}\n"
            formatted += f"SQL:\n{ex['query']}\n\n"
        
        return formatted


# Para usar como singleton
_selector_instance = None

def get_example_selector(k=3):
    """Obtiene o crea la instancia del selector"""
    global _selector_instance
    if _selector_instance is None:
        _selector_instance = SQLExampleSelector(k=k)
    return _selector_instance