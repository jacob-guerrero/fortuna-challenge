# Métricas y plan de evaluación — Etapa 5

> Este documento previo a implementar la suite y el baseline de ML.

## Alcance y supuestos

Se evalúan dos capacidades: clasificación de tickets y consulta RAG. El CSV
limpio contiene 19 variantes observadas, aunque el requerimiento de negocio
habla de 12. El baseline consolida esas variantes al catálogo operativo de 12
(por ejemplo, `Equipos` → `Hardware`, `Red` → `Conectividad` y `Reportes` →
`Informes`) y excluye `Sin Clasificar`, que no es una categoría operable. El
mapeo queda centralizado y probado para que sea una decisión auditable de
gobierno de datos.

## Umbrales definidos antes de implementar

| Capacidad | Métrica | Umbral | Motivo |
|---|---|---:|---|
| Clasificación | Macro F1 en conjunto de referencia | ≥ 0.75 | Evita que clases frecuentes oculten errores en clases pequeñas. |
| Clasificación | Precisión por categoría con al menos 3 casos | ≥ 0.70 | Detecta rutas que no deben automatizarse todavía. |
| Clasificación | Latencia p95 por ticket | ≤ 200 ms | El batch horario no exige tiempo real, pero debe ser eficiente. |
| RAG | Fidelidad de cita en preguntas con evidencia | 100 % | Toda respuesta debe citar documento, página y sección. |
| RAG | Abstención correcta fuera de dominio | ≥ 90 % | Es preferible escalar que inventar una política. |
| Orquestación | Tasa máxima de escalamiento inicial | ≤ 35 % | Se revisa después de calibrar RAG; no se fuerza una respuesta sin evidencia. |

## Conjunto de referencia

`reference_set.csv` contiene 59 casos, revisados manualmente antes de ejecutar
la suite. Incluye 39 casos de clasificación (tres por cada categoría operable)
y 20 preguntas
RAG, con preguntas sin evidencia. Cada fila conserva ID, entrada, resultado
esperado, fuente esperada cuando aplica y tipo de caso.

El conjunto no se usa para entrenar. Cualquier ticket usado en la referencia
se excluye del entrenamiento del baseline para evitar fuga de datos.

## Reglas de fallo de CI

La evaluación imprimirá métricas en JSON y terminará con código distinto de
cero si incumple un umbral. El reporte de métricas se conserva como artefacto
del job de CI. Un fallo no se corrige reduciendo el umbral sin una decisión
documentada.

La suite automatizada de esta entrega cubre el clasificador clásico, que es el
componente de IA evaluado en CI. Los 20 casos RAG quedan como conjunto de
calibración manual: ejecutar recuperación real en CI requeriría versionar el
índice y descargar embeddings, lo cual haría la suite frágil. Los contratos de
abstención y citas siguen cubiertos por las pruebas de Etapa 3.
