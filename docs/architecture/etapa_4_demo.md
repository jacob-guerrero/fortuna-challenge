# Ejecución de la demostración de Etapa 4

1. Configure `MOCK_API_TOKEN` en su `.env` local con el token indicado por el
   servicio mock.
2. En una terminal, inicie el segundo sistema:

   ```powershell
   .\venv\Scripts\python.exe -m uvicorn servicio_mock.app:app --port 8080
   ```

3. En otra, inicie la Mesa de Ayuda:

   ```powershell
   .\venv\Scripts\python.exe -m uvicorn src.api.main:app --port 8000
   ```

4. Envíe un evento al webhook propio:

   ```powershell
   $body = @{
     evento_id = "evt-demo-0001"
     tipo = "solicitud.recibida"
     solicitud = @{
       asunto = "Solicitud de vacaciones"
       descripcion = "¿Con cuánta anticipación debo solicitar vacaciones?"
       area = "Talento Humano"
       solicitante = "persona@empresa.co"
     }
   } | ConvertTo-Json -Depth 3
   Invoke-RestMethod http://localhost:8000/integraciones/mensajeria/webhook -Method Post -ContentType application/json -Body $body
   ```

Repita el mismo comando: la respuesta debe indicar `duplicate: true` y el
sistema no vuelve a notificar. Cambie el contenido sin cambiar `evento_id`: la
API responde 409. Si el segundo sistema falla tras sus reintentos, la respuesta
indica `delivery_pending: true`; el diseño de producción lo reintentaría desde
la outbox.

La demo usa estado en memoria para mostrar el contrato. El modelo persistente,
la estrategia de índices y el paso a outbox/worker están documentados en
[etapa_4_arquitectura.md](etapa_4_arquitectura.md).
