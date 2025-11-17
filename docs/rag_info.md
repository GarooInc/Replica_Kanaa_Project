# RAG (Retrieval Augmented Generation)

## Descripción general
En esta carpeta se gestiona toda la lógica de recuperación aumentada para los flujos del agente. El contexto se indexa mediante FAISS y se consulta usando embeddings de Cohere, lo que permite que el sistema recupere fragmentos relevantes para contestar de forma precisa y exhaustiva.

## Archivos clave
- **rag_indexer.py**: Código de indexación. Se encarga de procesar los archivos markdown/otros documentos, generar embeddings y almacenar el índice FAISS. Permite reindexar cuando cambian los datos.
- **rag_store.py**: Lógica de almacenamiento y recuperación del índice. Gestiona el retriever global e integra la consulta a la API (suele usarse en el evento lifespan de FastAPI).

## Uso recomendado
1. Coloca tus documentos contextuales en `app/data/`.
2. Ejecuta el endpoint `/contextrebuild` para indexar y generar el índice FAISS.
3. El sistema estará listo para hacer búsquedas precisas que soporten respuestas con contexto hotelero u otros datos.

## Detalles técnicos
- Utiliza embeddings Cohere por velocidad y precisión en campos turísticos/hoteleros.
- El endpoint de reconstrucción es crítico para mantener actualizado el contexto.

## Ampliaciones
Puedes mejorar el sistema para soportar otros formatos (PDF, HTML), segmentar la indexación por zonas de interés, agregar validaciones o métricas de cobertura semántica.

---