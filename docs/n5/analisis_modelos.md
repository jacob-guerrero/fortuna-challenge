# Comparación: ML clásico, LLM y RAG

## Recomendación

Usar ML clásico como ruta principal para clasificar R-01, RAG con respuesta
restringida por evidencia para R-02 y automatización tradicional para R-03. Un
LLM queda como fallback para tickets ambiguos o tareas generativas, no como
reemplazo de reglas deterministas.

| Criterio | ML clásico (R-01) | LLM (fallback/generación) | RAG (R-02) |
|---|---|---|---|
| Costo por 1.000 solicitudes | CPU marginal; sin costo por token | Variable por tokens del proveedor | Embeddings + tokens de redacción; controlar presupuesto |
| Latencia | p95 ≈ 0.5 ms en el baseline local | Segundos y dependiente del proveedor | Mayor que ML; aceptable para 80 consultas/día |
| Precisión / seguridad | Macro F1 1.00 en dataset sintético | Debe evaluarse con conjunto de referencia | Citas obligatorias y abstención sin evidencia |
| Mantenimiento | Reentrenar al cambiar taxonomía o aparecer drift | Mantener prompt, modelo y presupuesto | Reingestar al cambiar políticas y calibrar umbral |
| Mejor uso | Categorías estables y alto volumen | Casos ambiguos o redacción | Políticas cambiantes en lenguaje natural |

## Interpretación de costos

Para 3.000 tickets diarios, una llamada LLM por ticket multiplica el gasto por
token sin aportar una capacidad necesaria para una taxonomía estable. El
baseline clásico procesa texto localmente en CPU. Para RAG, el menor volumen
(80/día) permite pagar el costo de recuperación y redacción, siempre bajo el
presupuesto y las alertas definidos en Etapa 4.

No se publican precios fijos de proveedor: cambian con frecuencia. La estimación
operativa usa los tokens observados por la telemetría y tarifas configuradas por
ambiente, no valores codificados en la lógica.

## Limitaciones y siguiente decisión

El F1 perfecto no prueba desempeño futuro porque el histórico sintético repite
plantillas. Antes de automatización sin revisión se debe medir una muestra de
producción etiquetada manualmente y temporalmente separada. Si Macro F1 baja de
0.75, una categoría cae bajo 0.70 de precisión o cambia el catálogo, esa ruta
se envía a revisión humana/LLM y se reentrena el modelo. Esta es una decisión
de negocio y seguridad, no solo una optimización de métrica.
