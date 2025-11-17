# Streaming

## Descripción general
Todos los componentes de streaming en tiempo real del agente se encuentran aquí. El motor SSE permite enviar respuestas del modelo y resultados de herramientas de manera incremental, mejorando la experiencia de usuario y el monitoreo de workflows complejos.

## Componentes principales
- **streaming.py**: Implementa el motor SSE, permitiendo que los tokens generados por el modelo lleguen como eventos.
- **event_handler.py**: Estructura y formatea los eventos para el frontend o consumidor SSE.
- **lazy_loading.py**: Permite carga diferida de modelos y recursos, optimizando la performance inicial.
- **tool_execution.py**: Coordina la ejecución de herramientas y el logging de acciones, integrando los resultados al stream general.

## Ejemplo de flujo
- El usuario pregunta vía `/ask`.
- El sistema responde token a token, avisando cada uso de herramienta y finalizando con los resultados agregados.

## Cómo ampliar
Puedes agregar nuevos tipos de eventos, mejorar el parsing de errores, o integrar monitoreo con logs avanzados.

## Recomendaciones
Incluye pruebas unitarias para cada tipo de evento y asegura la compatibilidad con distintos frontends SSE.

---