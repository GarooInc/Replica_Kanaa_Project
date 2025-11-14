## Kaana Data Agent

Guía rápida de instalación y ejecución usando uv (gestor de paquetes/entornos ultrarrápido para Python).

### Requisitos

- Python 3.13 o superior (según `pyproject.toml`).
- uv instalado.
	- Windows (PowerShell):
		```powershell
		winget install Astral.Uv
		# Verificar
		uv --version
		```
	- Alternativa: pipx
		```powershell
		pipx install uv
		```

### Clonar el repositorio

```powershell
git clone https://github.com/GarooInc/kaana_data_agent.git
cd kaana_data_agent
```

### Crear y activar el entorno con uv

```powershell
# Crea el entorno virtual (por defecto en .venv)
uv venv .venv

# Activa el entorno en PowerShell
.\.venv\Scripts\Activate.ps1

# (Opcional) Establecer como entorno por defecto de uv en este proyecto
uv python pin
```

Si PowerShell bloquea la ejecución de scripts, puedes habilitarla (como administrador):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Instalar dependencias del proyecto

Este proyecto declara dependencias en `pyproject.toml`. Para instalarlas:

```powershell
# Instala/resolve dependencias según pyproject (+ lockfile si existe)
uv sync
```

Agregar nuevas dependencias (ejemplos):

```powershell
# Dependencia de runtime
uv add requests

# Dependencia de desarrollo
uv add --dev ruff pytest
```

Actualizar dependencias (resolver de nuevo):

```powershell
uv lock --upgrade
uv sync
```

### Variables de entorno

El proyecto incluye `python-dotenv`, por lo que puedes crear un archivo `.env` en la raíz para tus claves/configuraciones. Ejemplo:

```
# .env (ejemplo)
OPENAI_API_KEY=sk-...
COHERE_API_KEY=...
```

Si existe un `.env.example`, cópialo:

```powershell
Copy-Item .env.example .env
```

### Ejecutar la API (FastAPI + Uvicorn)

Hay una aplicación FastAPI en `main.py` con el objeto `app`. La forma más fiable de lanzarla es invocar Uvicorn apuntando a ese objeto directamente (evita ejecutar `python main.py` si no es necesario):

```powershell
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Documentación interactiva: http://localhost:8000/docs
- Esquema OpenAPI: http://localhost:8000/openapi.json

Endpoint principal disponible:

- POST `/ask` — cuerpo JSON: `{ "question": "...", "message_history": [] }`

Prueba rápida desde PowerShell con Invoke-RestMethod:

```powershell
$body = @{ question = "Hola, ¿cómo estás?"; message_history = @() } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/ask -Method Post -Body $body -ContentType 'application/json'
```

Nota sobre streaming: el endpoint `/ask` devuelve eventos tipo Server-Sent Events (SSE) para streaming de tokens. Para probar SSE, usa un cliente compatible (por ejemplo, un frontend o `curl`/`wget` desde un entorno que no sea PowerShell) o herramientas como `Postman` con soporte de SSE.

### Comandos útiles con uv

```powershell
# Ejecutar un script/comando dentro del entorno (sin activar)
uv run python -V

# Listar paquetes instalados
uv pip list

# Limpiar caché de uv
uv cache clean
```

### Estructura del proyecto (resumen)

```
main.py                      # Punto de entrada FastAPI (objeto app)
app/
	streaming/
		streaming.py             # Lógica de streaming SSE
		event_handler.py         # Utilidades para formatear eventos SSE
	utilities/
		photo_uploader.py        # Utilidad para subir imágenes
```

### Problemas conocidos / notas

- El archivo `pyproject.toml` requiere Python >= 3.13. Asegúrate de tener esa versión disponible (uv la gestionará si está instalada). Si necesitas instalar Python 3.13 en Windows:
	```powershell
	winget install Python.Python.3.13
	```
- Si prefieres ejecutar con hot-reload, usa `--reload` como en el comando de ejemplo.

### Desarrollo y pruebas (opcional)

```powershell
# Añadir herramientas de desarrollo
uv add --dev pytest ruff

# Lanzar tests (si existen)
uv run pytest -q

# Lint (ejemplo con ruff)
uv run ruff check .
```

---

Hecho con uv y FastAPI 🚀

## Arquitectura y módulos

### Visión general

El proyecto implementa una API de FastAPI que expone:

- `POST /ask`: genera respuestas con streaming de tokens vía Server‑Sent Events (SSE) usando LangChain + OpenAI.
- `PUT /contextrebuild`: reindexa contenido Markdown en un índice FAISS para Retrieval‑Augmented Generation (RAG).

Durante el ciclo de vida de la app, se inicializa un retriever global (FAISS + Cohere Embeddings) que alimenta la herramienta de contexto del hotel. El flujo de streaming sigue un esquema ReAct: el modelo puede invocar herramientas, consumir sus resultados y luego producir una respuesta final en streaming.

### Estructura por paquetes

- `main.py`
	- Crea la app FastAPI y configura `lifespan` para inicializar el retriever global.
	- Endpoint `PUT /contextrebuild`: reconstruye el índice FAISS desde archivos Markdown subidos y actualiza el retriever global.
	- Endpoint `POST /ask`: devuelve una `StreamingResponse` que emite eventos SSE desde `app/streaming/streaming.py`.

- `app/streaming/`
	- `streaming.py`: corazón del flujo SSE. Implementa `ask_streaming()` (async generator) con:
		- Construcción de historial con `SystemMessage`, historial previo y la pregunta del usuario.
		- LLM `ChatOpenAI` con `streaming=True` y herramientas vinculadas (lazy) vía `bind_tools()`.
		- Bucle ReAct con máx. `max_iterations` (por defecto 8) para manejar tool calls:
			- Sin tool calls: hace streaming de la respuesta final (`answer`) y termina (`done`).
			- Con tool calls: ejecuta herramientas (ver `tool_execution.py`), agrega `ToolMessage` al historial, emite eventos de uso (`tool_usage`) y continúa iterando.
			- Registra bitácora de herramientas en `tool_log` (incluida al final si hubo herramientas).
			- Maneja errores por iteración y globales, emitiendo un `answer` genérico y `done`.
		- Integración opcional de imágenes: intenta subir la primera imagen encontrada en el repo (ver `photo_uploader.py`) y agrega un markdown `![image](URL)` al final de la respuesta.
	- `event_handler.py`: utilidades para formatear eventos SSE.
		- `send_event(event_type, data)`: emite líneas SSE `event:` y `data:` con `data` codificado como JSON y sello de tiempo.
		- `send_error(message, code)`: atajo que emite un evento `error` con `{ error, code? }`.
		- `send_done()`: evento final `done` con `{}`.
	- `lazy_loading.py`: configuración y bind perezoso del LLM.
		- Instancia global de `ChatOpenAI` (`model="gpt-4o"`, `streaming=True`).
		- `bind_tools(tools, force_rebind=False)`: cachea la instancia enlazada a herramientas para evitar rebinds innecesarios. Registra un warning si cambia la huella de herramientas.
	- `tool_execution.py`: envoltorio para ejecutar herramientas y registrar su estado en `tool_log`.
		- Soporta `ainvoke(...)` (async) y `run(...)` (sync). Registra `started`, `completed` o `error` con detalles.

- `app/agent_tools/`
	- `rag_tool.py`: construye la herramienta `hotel_context_search` con `create_retriever_tool(...)` a partir del retriever global. Inicialización perezosa y segura.
	- `tool_getter.py`: ensambla la lista de herramientas del agente: `hotel_context_search` (si disponible) y `strategic_web_search` (Tavily).
	- `websearch_tool.py`: integra `TavilySearch` como herramienta `strategic_web_search` y define su `args_schema` (Pydantic).

- `app/rag/`
	- `rag_indexer.py`: indexador de Markdown → FAISS.
		- Parseo jerárquico de secciones (encabezados), segmentación con `RecursiveCharacterTextSplitter`, embeddings `CohereEmbeddings` (`embed-multilingual-light-v3.0`).
		- Persiste `FAISS` y `chunk_store.json` en `app/data/hotel_context_faiss_index/`.
		- `index_markdown_contents(..., rebuild=True|False)` para reconstrucción o actualización incremental.
	- `rag_store.py`: gestión del índice y retriever global.
		- `load_vectorstore()`, `get_retriever(k)`, `set_global_retriever(...)`, `get_global_retriever()`.
		- `initialize_hotel_context_tool()` para inicializar explícitamente la tool RAG si se requiere.

- `app/prompt/enhanced_prompt.py`
	- `get_enhanced_prompt(question, tools)` devuelve un prompt base con instrucciones de estilo de respuesta (Markdown, idioma, veracidad, etc.).
	- Hooks `check_for_tools(...)` y `check_for_fshotexamples(...)` (placeholders) para enriquecer dinámicamente el prompt.

- `app/utilities/photo_uploader.py`
	- `upload_first_photo_found()`: busca la primera imagen en el repo (excluye carpetas comunes), la sube al servidor y retorna la URL. Se usa opcionalmente en streaming para adjuntar una imagen al final.

### Streaming: eventos SSE y consumo

`/ask` retorna una respuesta con `media_type: text/event-stream`. Los eventos emitidos son:

- `answer`: contenido parcial o final del modelo. `data` es JSON con `content` y `timestamp`.
- `tool_usage`: mensajes informativos sobre el uso/estado de una herramienta.
- `tool_log`: bitácora al final del flujo con entradas `{ iteration, tool_name, tool_args, status, error? }`.
- `error`: error estándar con `{ error, code? }`.
- `done`: marca el fin del stream. `data` es `{}`.

Formato SSE por línea:

```
event: <tipo>
data: { ...json... }

```

Ejemplo de consumo con `curl` (PowerShell no maneja bien SSE interactivo):

```bash
curl -N -X POST http://localhost:8000/ask \
	-H "Content-Type: application/json" \
	-d '{"question":"¿Qué amenidades ofrece el hotel?","message_history":[]}'
```

### Flujo lógico de `ask_streaming()`

1. Construye historial (System + historial previo + pregunta actual).
2. Enlaza herramientas disponibles de forma perezosa (`bind_tools`).
3. Itera hasta `max_iterations`:
	 - Si no hay tool calls: hace streaming de la respuesta final (`answer`), opcionalmente agrega una imagen, emite `tool_log` si aplica y cierra con `done`.
	 - Si hay tool calls: ejecuta cada herramienta (`execute_tool`), añade `ToolMessage` al historial, emite `tool_usage` y continúa.
	 - Si hay error: emite `answer` genérico y `done`.
4. Si se agotan iteraciones: fuerza una respuesta final en streaming y cierra.

### Añadir nuevas herramientas

1. Implementa la herramienta compatible con LangChain (`run(...)` o `ainvoke(...)`).
2. Declara su `name` y `description` (y `args_schema` si recibe parámetros estructurados).
3. Expórtala desde `app/agent_tools/<tu_tool>.py`.
4. Agrégala en `app/agent_tools/tool_getter.py` para que `get_agent_tools()` la incluya y quede disponible para el modelo.

### Variables de entorno necesarias

- `OPENAI_API_KEY`: requerido por `langchain_openai`.
- `COHERE_API_KEY`: requerido por `CohereEmbeddings` (RAG).
- `TAVILY_API_KEY`: requerido por `TavilySearch` (búsqueda web).

Puedes gestionarlas en `.env` (cargado automáticamente por `python-dotenv`).

### Notas y buenas prácticas

- Para el streaming, consume eventos SSE con clientes compatibles (navegador/FetchEventSource, `curl -N`, Postman con SSE, etc.).
- Si reindexas con `/contextrebuild`, el retriever global y la tool RAG se actualizan automáticamente.
- `bind_tools` cachea el LLM enlazado a herramientas; si cambias la lista de tools en caliente, considera `force_rebind=True` (ajuste por código si lo necesitas).

