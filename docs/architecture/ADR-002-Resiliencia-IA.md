# ADR-002: Degradación controlada ante fallos del proveedor de IA

## Estado

Aceptada. Los reintentos y el modo degradado están implementados; el circuit
breaker es la evolución prevista para producción.

## Contexto

El proveedor LLM puede agotar el tiempo de espera, responder 429 o fallar con
5xx. Propagar esos errores dejaría solicitudes sin atender; reintentar sin
límite empeoraría la saturación y el costo.

## Decisión

Se reintentan errores transitorios con backoff exponencial y un máximo de
intentos. Si no se obtiene respuesta, se crea el ticket con categoría
`Pendiente Clasificación Manual`, prioridad `Media` y una respuesta transparente
para la persona solicitante. En producción se añadirá un circuit breaker
configurable por ambiente para cortar llamadas mientras el proveedor se
recupera.

## Alternativas consideradas

1. **Propagar el error del LLM al cliente.** Descartada porque un proveedor no
   debe impedir registrar ni escalar una solicitud.
2. **Reintentos ilimitados.** Descartada porque aumenta latencia, costo y la
   probabilidad de agravar un rate limit.
3. **Reintentos limitados, fallback y circuit breaker.** Elegida porque
   conserva disponibilidad y protege al proveedor sin ocultar la degradación.

## Consecuencias

### Beneficios

- Los tickets se registran y se enrutan incluso cuando falla la IA.
- El backoff reduce presión sobre dependencias con fallos transitorios.

### Trade-offs

- El modo degradado aumenta la carga de revisión humana.
- El circuit breaker exige métricas y calibración de sus umbrales antes de
  activarlo en producción.
