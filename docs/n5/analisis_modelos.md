# Análisis Estratégico: Machine Learning Clásico vs LLMs para Clasificación

**Destinatario:** CTO / Dirección Técnica  
**Autor:** Tech Lead  
**Asunto:** Criterios técnicos para la selección y evolución de nuestra arquitectura de Inteligencia Artificial.  

---

## 1. Contexto Ejecutivo
La actual implementación en *La Fortuna S.A.* utiliza Large Language Models (LLMs) complementados con RAG para clasificar tickets y extraer políticas de cumplimiento. A medida que proyectamos procesar más de 10.000 tickets diarios, es imperativo evaluar de forma objetiva si un modelo de Machine Learning Tradicional (ML Clásico) es una alternativa técnica y financieramente superior para ciertas tareas.

## 2. Matriz de Comparación Técnica

| Criterio Estratégico | Machine Learning Clásico (ej. Random Forest, SVM, Regresión) | Grandes Modelos de Lenguaje (LLMs) (ej. GPT-4o, Llama 3) |
|----------------------|--------------------------------------------------------------|----------------------------------------------------------|
| **Costo por inferencia (Opex)** | **Extremadamente bajo.** Puede ejecutarse en CPUs económicas. | **Alto.** Costo por token (APIs) o infraestructura GPU muy cara si es on-premise. |
| **Latencia / Velocidad** | **Milisegundos** (~10-50ms). | **Segundos** (~1000-3000ms). |
| **Determinismo** | Altamente determinista y matemático. | Probabilístico, propenso a alucinaciones. |
| **Capacidad Generativa** | **Nula.** Solo clasifica y predice etiquetas estáticas. | **Alta.** Capaz de resumir texto, redactar respuestas humanas y hacer RAG. |
| **Necesidad de Datos (Cold Start)** | Requiere miles de tickets históricos correctamente etiquetados y limpios. | Funciona en *Zero-Shot* mediante prompts explicativos, sin historial previo. |
| **Mantenimiento Operativo** | Requiere procesos MLOps para reentrenamiento continuo ante *Data Drift* (nuevas categorías). | Mantenimiento ágil basado en ajuste de prompts (Prompt Engineering) y actualización de base RAG. |

## 3. ¿En qué casos abandonaríamos el LLM por ML Clásico?
Recomiendo migrar total o parcialmente hacia modelos tradicionales (ML Clásico) bajo los siguientes escenarios:
1. **La funcionalidad de RAG ya no aporta valor:** Si el negocio decide que "responder al usuario con políticas" y generar "resúmenes técnicos" ya no son requeridos, usar un LLM exclusivamente para predecir si un ticket es "Hardware" o "Accesos" es un desperdicio (Overkill arquitectónico).
2. **Madurez de los datos históricos:** Contamos con un dataset impecable de cientos de miles de tickets y las taxonomías de área/categoría rara vez cambian.
3. **Optimización extrema de costos (FinOps):** El volumen escala por encima de 50.000 tickets/día y el margen operativo se ve erosionado por la factura mensual del proveedor LLM.
4. **SLA de latencia estricto:** El sistema requiere que la clasificación sea completamente síncrona, en tiempo real, bloqueando interfaces web que demandan tiempos de respuesta inferiores a los 200ms.

## 4. Recomendación Final (El Camino a Seguir)
Para la actual fase de descubrimiento, validación e impacto al empleado, el **LLM con RAG es la opción ideal** por su versatilidad inmediata sin requerir un pipeline complejo de Data Science.

A mediano plazo (al superar la marca de los 10K tickets), sugiero transicionar hacia una **Arquitectura Híbrida (Ensemble)**:
- Un modelo ligero y barato de ML clásico predice velozmente la `categoría` y `prioridad` como capa de enrutamiento frontal.
- Se reserva y rutea hacia el LLM solo el "Modo Experto": tickets ambiguos, análisis de políticas y tareas de generación de resúmenes, balanceando así los costos de infraestructura mientras se maximiza la inteligencia y el SLA.
