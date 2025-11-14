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

