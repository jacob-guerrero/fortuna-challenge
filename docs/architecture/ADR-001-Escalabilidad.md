# ADR-001: Procesamiento asíncrono para escalar tickets

## Estado

Aceptada para la arquitectura objetivo de la Etapa 4. La demostración local
conserva un flujo síncrono mínimo.

## Contexto

Un ticket puede requerir clasificación LLM, recuperación RAG y una notificación
al segundo sistema. Ejecutar todo dentro de la petición HTTP ata el tiempo de
respuesta a dependencias remotas y limita la capacidad ante picos de carga.

## Decisión

En producción, la API validará y persistirá el ticket con estado `Recibido`,
publicará un mensaje y devolverá `202 Accepted`. Workers independientes
ejecutarán la orquestación y actualizarán el resultado. La notificación al
cliente se realizará por consulta de estado o, si se requiere, SSE.

## Alternativas consideradas

1. **Procesar todo síncronamente en la API.** Descartada para producción porque
   la latencia y los fallos de LLM/RAG afectarían el SLA de recepción. Se usa
   únicamente en la demo para mantenerla ejecutable sin infraestructura extra.
2. **Usar un cron que consulte tickets pendientes.** Descartada porque agrega
   latencia innecesaria y responde mal a picos.
3. **Cola y workers desacoplados.** Elegida porque permite nivelar carga,
   reintentar sin perder tickets y escalar consumidores de forma independiente.

## Consecuencias

### Beneficios

- La recepción se mantiene rápida y disponible ante degradaciones del proveedor.
- Los picos se absorben en la cola y los workers se escalan horizontalmente.

### Trade-offs

- El resultado final tiene consistencia eventual.
- Se incorporan operación, monitoreo y costo de un broker y workers.
