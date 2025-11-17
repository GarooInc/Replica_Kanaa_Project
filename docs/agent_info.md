# Agent Tools

## Descripción general
En esta carpeta se encuentran todas las herramientas disponibles para el agente de datos. Cada módulo representa una integración, funcionalidad específica o herramienta externa que el sistema puede invocar durante el procesamiento de preguntas y flujos de trabajo inteligentes.

## Estructura de la carpeta
- **tool_getter.py**: Punto central para registrar y gestionar las herramientas del agente. Aquí se importan y exponen todas las herramientas que podrán ser utilizadas en las cadenas de razonamiento y respuesta.
- **websearch_tool.py**: Implementación para búsquedas web utilizando la API de Tavily. Puedes extender o modificar el sistema para funcionar con otros motores de búsqueda.

Otros módulos aquí pueden incluir integraciones con servicios externos (rest, bases de datos, scraping, APIs hoteleras, etc.)

## Uso típico
Cada herramienta expuesta en esta carpeta puede ser referenciada en los prompts del modelo, usada por LangChain durante el workflow o invocada directamente por endpoints de FastAPI.

## Cómo agregar una nueva herramienta
1. Crea un nuevo archivo Python con la implementación.
2. Exporta la herramienta en `tool_getter.py`.
3. Documenta su uso y parámetros.
4. Agrega ejemplos aquí para el equipo, incluyendo formato de argumentos y resultados esperados.

## Ejemplo de extensión
Si necesitas una herramienta de geolocalización, crea `geo_tool.py`, expórtala y actualiza este README con su documentación.

## Buenas prácticas
- Usa args_schema para definir parámetros en las herramientas.
- Incluye siempre ejemplos de request y response para facilitar la integración y testing.

---