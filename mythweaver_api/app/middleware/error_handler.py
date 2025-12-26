"""
Error Handling Middleware for Mythweaver API

Provides centralized exception handling with structured logging and 
standardized error responses for all API endpoints.
"""

import traceback
import logging
from datetime import datetime
from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions import MythweaverException


# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """
    Middleware to catch and handle all exceptions in a standardized way.
    
    Logs errors with context and returns consistent JSON error responses.
    """
    try:
        response = await call_next(request)
        return response
    
    except MythweaverException as exc:
        # Handle custom Mythweaver exceptions
        logger.warning(
            f"Mythweaver Exception: {exc.error_code} - {exc.detail}",
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code or "MYTHWEAVER_ERROR",
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
            }
        )
    
    except StarletteHTTPException as exc:
        # Handle FastAPI/Starlette HTTP exceptions
        logger.warning(
            f"HTTP Exception: {exc.status_code} - {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP_ERROR",
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
            }
        )
    
    except RequestValidationError as exc:
        # Handle Pydantic validation errors
        logger.warning(
            f"Validation Error: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors(),
            }
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors(),
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
            }
        )
    
    except Exception as exc:
        # Handle unexpected exceptions
        logger.error(
            f"Unexpected Error: {type(exc).__name__} - {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc(),
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
            }
        )


def setup_error_handlers(app):
    """
    Register custom exception handlers for specific exception types.
    
    This provides an alternative to middleware for handling exceptions.
    """
    
    @app.exception_handler(MythweaverException)
    async def mythweaver_exception_handler(request: Request, exc: MythweaverException):
        logger.warning(
            f"Mythweaver Exception: {exc.error_code} - {exc.detail}",
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "path": request.url.path,
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code or "MYTHWEAVER_ERROR",
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            f"Validation Error on {request.url.path}",
            extra={"errors": exc.errors()}
        )
        
        # Convert error objects to strings in the error details
        errors = exc.errors()
        for error in errors:
            if 'ctx' in error and 'error' in error['ctx']:
                error['ctx']['error'] = str(error['ctx']['error'])
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": errors,
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unexpected Error: {type(exc).__name__}",
            extra={
                "path": request.url.path,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
            }
        )
