import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.routers import tickets
from src.core.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Mesa de Ayuda Inteligente - API", version="1.0.0")

app.include_router(tickets.router)

def error_response(status_code: int, error: str, message: str, path: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": error, "message": message, "path": path})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(422, "validation_error", "La solicitud contiene datos inválidos.", request.url.path)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    message = exc.detail if isinstance(exc.detail, str) else "La solicitud no pudo procesarse."
    error = "not_found" if exc.status_code == 404 else "http_error"
    return error_response(exc.status_code, error, message, request.url.path)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Excepción no controlada", extra={"event": "unhandled_exception"})
    return error_response(500, "internal_server_error", "Ha ocurrido un error inesperado en el servidor.", request.url.path)
