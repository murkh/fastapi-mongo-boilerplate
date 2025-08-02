import traceback
from fastapi import Request
from fastapi.responses import JSONResponse


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for all unhandled exceptions.
    Returns a 500 Internal Server Error with stack trace.
    """
    stack_trace = traceback.format_exc()
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error": str(exc),
            "stack_trace": stack_trace
        }
    )


def setup_exception_handlers(app):
    """
    Setup exception handlers for the FastAPI application.
    """
    app.add_exception_handler(Exception, general_exception_handler)
