# semantic_search_find.py
"""
Carga el índice FAISS existente y realiza búsqueda semántica pura.
"""

import os, logging
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings
from dotenv import load_dotenv

# ================= CONFIG =================
load_dotenv()
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.join(os.path.dirname(__file__), "../data/semantic_search_faiss_index")
INDEX_NAME = "account_index"
INDEX_PATH = os.path.join(BASE_DIR, INDEX_NAME)
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# ================= EMBEDDINGS =================
embedding_model = CohereEmbeddings(
    model="embed-multilingual-light-v3.0",
    cohere_api_key=COHERE_API_KEY
)

# ================= CARGA DEL ÍNDICE =================
try:
    # Add logging to verify the exact path being used for the FAISS index.
    logging.info(f"Verificando ruta del índice FAISS")
    
    vs = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)
    logging.info(f"Indice FAISS cargado")
except Exception as e:
    vs = None
    logging.error(f"❌ No se pudo cargar el índice FAISS: {e}")

# ================= FUNCIONES =================
def semantic_search(query: str, k: int = 5):
    """Busca las cuentas más similares semánticamente."""
    if not vs:
        logging.error("El índice FAISS no está disponible.")
        return []
    try:
        results = vs.similarity_search_with_score(query, k=k)
        seen = set()
        formatted = []
        for doc, score in results:
            name = doc.metadata.get("account_name") if doc.metadata else None
            if not name:
                name = getattr(doc, "page_content", "(sin contenido)")
            if name not in seen:
                seen.add(name)
                formatted.append({
                    "account_name": str(name),
                    "score": round(float(score), 5)
                })
        return sorted(formatted, key=lambda x: x["score"])
    except Exception as e:
        logging.error(f"⚠️ Error en búsqueda semántica: {e}")
        return []

# ================= CLI =================
if __name__ == "__main__":
    print("Modo interactivo: Búsqueda semántica de cuentas (FAISS + Cohere)")
    print("Escribe 'exit' para salir.\n")

    while True:
        q = input("🔍 Buscar: ").strip()
        if not q or q.lower() in {"exit", "quit"}:
            print("👋 Saliendo...")
            break

        matches = semantic_search(q)
        if not matches:
            print("⚠️ Sin resultados.\n")
            continue

        print("\nResultados:")
        for i, m in enumerate(matches, 1):
            print(f"  {i}. {m['account_name']} (score={m['score']})")
        print("\n" + "-" * 50 + "\n")
