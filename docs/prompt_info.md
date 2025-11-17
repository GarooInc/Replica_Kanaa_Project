# Prompt

## Descripción general
Esta carpeta contiene la lógica de construcción, formateo y mejora de los prompts que se utilizan en todos los flujos del agente de datos. Aquí se definen las instrucciones, plantillas y mecanismos avanzados para la interacción con modelos LLM.

## Componentes principales
- **enhanced_prompt.py**: Script fundamental para crear prompts mejorados. Incluye plantillas condicionadas, instrucciones contextuales y hooks que permiten modificar el prompt de manera dinámica según el flujo o los eventos del usuario.

## Ejemplos de uso
Puedes definir prompts para distintas tareas, como:
- Preguntas frecuentes de hotel
- Procesamiento semántico avanzado
- Invocación de herramientas condicional

## Cómo personalizar
- Modifica las plantillas para cambiar el tono, nivel de detalle o instrucciones específicas.
- Agrega hooks dinámicos para añadir datos del contexto de manera automatizada.

## Recomendaciones
Es recomendable mantener versiones y comentarios en los prompts para facilitar el tracking de cambios y evolución de los flujos de interacción.

---