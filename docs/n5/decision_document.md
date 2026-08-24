# Documento de decisión — Etapa 5

## R-01: Clasificación de solicitudes entrantes

**Decisión: automatización tradicional con ML clásico.**

El histórico etiquetado, las categorías estables y el procesamiento por lotes
favorecen un clasificador supervisado de texto. Un modelo TF-IDF + regresión
logística es barato de ejecutar en CPU, tiene latencia baja y se puede medir
con precisión por categoría. Un LLM se reserva como fallback para casos de baja
confianza o para categorías nuevas, no como ruta principal.

| Criterio | Evaluación |
|---|---|
| Volumen | 3.000/día favorece bajo costo por inferencia. |
| Estabilidad | 12 categorías estables por tres años; el problema es supervisado. |
| Latencia | El lote horario elimina la ventaja generativa de un LLM. |
| Error | Es reversible y no afecta directamente al usuario. |
| Mantenimiento | Reentrenamiento al cambiar catálogo o degradarse la métrica. |

**Cambiaría la decisión** si desaparece el histórico etiquetado, aparecen
categorías con frecuencia o se requiere redactar una respuesta personalizada;
en ese caso usaría LLM como fallback o enfoque híbrido.

## R-02: Consulta de políticas internas

**Decisión: solución combinada RAG + LLM de redacción restringida.**

La consulta es lenguaje natural y las políticas cambian poco, por lo que RAG
recupera los fragmentos actualizados sin reentrenar un modelo. El LLM solo
puede redactar desde los fragmentos recuperados y debe conservar las citas. Si
no hay evidencia o la similitud es baja, el sistema se abstiene y escala.

| Criterio | Evaluación |
|---|---|
| Volumen | 80/día hace sostenible el costo controlado por tokens. |
| Riesgo | Montos y plazos erróneos generan reclamaciones; citas y abstención son obligatorias. |
| Latencia | Segundos es aceptable para una consulta no transaccional. |
| Mantenimiento | Al cambiar una política se reingesta el PDF; no se reentrena. |

**Cambiaría la decisión** a búsqueda tradicional si las preguntas se reducen a
un catálogo fijo de FAQs; a atención humana si la recuperación no logra la
precisión acordada aun después de calibrar umbrales.

## R-03: Recordatorio de tickets sin gestión

**Decisión: automatización tradicional, sin IA.**

La regla es determinista: contar tres o cinco días hábiles sin transición de
estado y enviar una plantilla. Un job diario idempotente consulta la base de
datos y registra una clave única por ticket, tipo de aviso y fecha programada.
No hay lenguaje ambiguo que un modelo necesite interpretar.

| Criterio | Evaluación |
|---|---|
| Volumen y latencia | Job diario a las 8:00 a. m.; un LLM agrega costo y puntos de fallo. |
| Error | Un duplicado afecta confianza; idempotencia SQL lo controla. |
| Mantenimiento | Calendario laboral y plantilla versionados son suficientes. |

**Cambiaría la decisión** solo si se pide interpretar conversaciones, priorizar
por riesgo no estructurado o redactar mensajes personalizados. Aun entonces la
regla de elegibilidad e idempotencia seguiría siendo tradicional.
