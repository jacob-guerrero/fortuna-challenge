# ADR-003: Idempotencia y entrega confiable entre sistemas

## Estado

Aceptada para el contrato de integración. La demo implementa su semántica con
un registro en memoria; producción la persistirá en la base relacional.

## Contexto

El segundo sistema puede reenviar webhooks, entregarlos fuera de orden o fallar
al recibir la notificación de vuelta. Sin una identidad estable, los reintentos
pueden duplicar tickets, escalaciones o mensajes.

## Decisión

Cada webhook debe incluir un `evento_id`. Se guarda junto con el hash del
payload: el mismo ID y contenido se reconoce como duplicado; el mismo ID con
contenido diferente es un conflicto. En producción, el cambio del ticket y el
evento de salida se confirmarán con una outbox en la misma transacción. Un
worker entregará la notificación con backoff exponencial.

## Alternativas consideradas

1. **Reintentar HTTP sin persistir eventos.** Descartada porque no evita efectos
   de negocio duplicados ni permite auditar entregas.
2. **Deduplicar únicamente en memoria.** Descartada para producción porque se
   pierde al reiniciar y no funciona con múltiples instancias; se usa en la demo
   para validar el contrato sin añadir una base de datos.
3. **`evento_id`, restricción única y outbox.** Elegida porque permite entrega
   al menos una vez con efectos idempotentes y trazabilidad de cada intento.

## Consecuencias

### Beneficios

- Los reintentos no duplican el procesamiento ni la notificación del evento.
- Se puede consultar estado, número de intentos y correlación de punta a punta.

### Trade-offs

- La entrega al segundo sistema es eventualmente consistente.
- La outbox requiere un worker, limpieza/retención de eventos y monitoreo.
