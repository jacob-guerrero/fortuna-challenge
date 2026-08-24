# Línea base de ML clásico — Etapa 5

## Objetivo y método

Se evaluó R-01 con un baseline reproducible: TF-IDF de unigramas y bigramas,
seguido de regresión logística con balanceo de clases. El texto de entrada es
`asunto + descripcion`. Antes de entrenar, las 19 variantes históricas se
consolidan al catálogo de 12 categorías operables y se excluye `Sin Clasificar`.

La partición es estratificada, 80 % entrenamiento y 20 % prueba, con
`random_state=42`. Resultado de `python -m scripts.evaluate_classic_baseline`:

| Métrica | Resultado |
|---|---:|
| Tickets utilizables | 1.893 |
| Entrenamiento / prueba | 1.514 / 379 |
| Macro F1 | 1.00 |
| Latencia p95 de predicción | ≈ 0.5 ms en entorno local |

## Matriz de confusión

Filas: etiqueta real. Columnas: predicción. La matriz resultó diagonal en esta
partición; los soportes por categoría fueron:

| Categoría | Casos correctos / casos de prueba |
|---|---:|
| Accesos | 59 / 59 |
| Aplicaciones | 59 / 59 |
| Capacitación | 16 / 16 |
| Compras | 24 / 24 |
| Conectividad | 34 / 34 |
| Hardware | 46 / 46 |
| Incidentes | 28 / 28 |
| Informes | 24 / 24 |
| Nómina | 27 / 27 |
| Otros | 20 / 20 |
| Vacaciones | 22 / 22 |
| Viáticos | 20 / 20 |

## Lectura de negocio y limitaciones

El baseline es adecuado para procesar lotes horarios a bajo costo y puede ser
la ruta principal de R-01. Sin embargo, no se debe prometer F1=1.00 en
producción: el dataset sintético tiene asuntos repetidos y plantillas de texto
muy similares entre entrenamiento y prueba. Antes de automatizar decisiones
sin revisión se requiere una muestra temporal y manualmente etiquetada de
producción, monitoreo de drift y una política de fallback para baja confianza.

El script guarda la matriz completa y las métricas en
`tmp/stage5_classic_baseline.json`; el archivo no se versiona porque es un
artefacto generado.
