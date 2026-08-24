# Revisión de `pr_para_revision.diff` — Etapa 5

## Resumen

No aprobaría el cambio. Expone un secreto, permite inyección SQL y combina
reporte, acceso a datos, llamadas LLM y actualización de tickets dentro de una
transacción larga. Debe corregirse antes de integrar.

| Severidad | Hallazgo | Evidencia | Corrección requerida |
|---|---|---|---|
| Crítica | Secreto versionado | `OPENAI_API_KEY = "sk-..."` | Revocar la clave, eliminarla del historial y leerla desde gestor de secretos/variable de entorno. |
| Crítica | Inyección SQL | Fechas, `area_filtro`, correo y categoría se concatenan en SQL | Usar consultas parametrizadas y validar tipos; nunca interpolar entrada de usuario. |
| Alta | Transacción durante llamadas remotas | `conn.begin()` ocurre antes de consultas y `requests.post` | Mantener la transacción solo para cambios atómicos; clasificar fuera de ella o usar cola/outbox. |
| Alta | LLM sin contrato ni control de fallos | Se accede directamente a `choices[0]` sin timeout, reintento ni validación | Usar el adaptador `LLMPort`, timeout, reintentos limitados, respuesta estructurada y fallback. |
| Media | N+1 queries | Tres consultas adicionales por ticket dentro del ciclo | Traer áreas, adjuntos e historial con joins/agregaciones o consultas agrupadas. |
| Media | División por cero | `suma_dias / contador_dias` | Devolver `None` o cero documentado cuando no haya tickets cerrados. |
| Media | Exportación CSV insegura | Se concatena texto sin escapar | Usar un escritor CSV que escape comas, comillas y fórmulas de hoja de cálculo. |
| Media | Parámetros no aplicados | `incluirCerrados` filtra después de calcular totales | Aplicar el filtro en la consulta o aclarar que los totales son globales. |

## Pruebas mínimas antes de aprobar

1. Entrada de SQL maliciosa no altera la consulta ni devuelve datos ajenos.
2. Falla o timeout del LLM conserva el ticket y lo deja para clasificación
   manual.
3. Reporte sin tickets cerrados no genera excepción.
4. Exportación con coma, comilla y valor que inicia con `=` se serializa segura.
5. El reporte ejecuta un número acotado de consultas para 100 tickets.

El estándar existente en `docs/ai_engineering_standard.md` aplica a este cambio:
se permite usar IA para andamiaje, pero secretos, SQL, validación, pruebas y
fallos del proveedor se revisan siempre antes de aceptar código generado.
