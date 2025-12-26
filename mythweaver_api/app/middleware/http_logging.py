"""
HTTP Request/Response Logging Middleware

Clean, efficient middleware for logging HTTP requests and responses with:
- Health endpoint exclusion
- Proper body handling
- Request ID tracking
- Structured JSON logging
"""
import json
import time
import logging
from typing import Any, Dict, Set
from starlette.types import ASGIApp, Receive, Scope, Send
from fastapi import Request

from ..core.logging_config import generate_request_id, set_request_id


class HTTPLoggingMiddleware:
    """ASGI middleware for logging HTTP requests and responses."""
    
    # Endpoints to exclude from logging
    EXCLUDED_PATHS: Set[str] = {"/health", "/metrics", "/favicon.ico"}
    
    # Maximum body size to log (in bytes)
    MAX_BODY_SIZE: int = 2000
    
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup HTTP requests logger."""
        logger = logging.getLogger("http_requests")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.propagate = False
        
        return logger
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI middleware entry point."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check if path should be excluded from logging
        path = scope.get("path", "")
        if path in self.EXCLUDED_PATHS:
            await self.app(scope, receive, send)
            return
        
        # Generate request ID and start timing
        request_id = generate_request_id()
        set_request_id(request_id)
        start_time = time.time()
        
        # Capture request and response data
        request_body = b""
        response_body = b""
        response_info: Dict[str, Any] = {}
        
        # Wrap receive to capture request body
        async def receive_wrapper():
            nonlocal request_body
            message = await receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                if len(request_body) + len(body) <= self.MAX_BODY_SIZE:
                    request_body += body
            return message
        
        # Wrap send to capture response
        async def send_wrapper(message):
            nonlocal response_body, response_info
            
            if message["type"] == "http.response.start":
                response_info["status_code"] = message["status"]
                response_info["headers"] = message.get("headers", [])
            
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body and len(response_body) + len(body) <= self.MAX_BODY_SIZE:
                    response_body += body
                
                # Log when response is complete
                if not message.get("more_body", False):
                    process_time = time.time() - start_time
                    await self._log_transaction(
                        scope, request_body, response_info, 
                        response_body, process_time, request_id
                    )
            
            await send(message)
        
        # Process request through the app
        await self.app(scope, receive_wrapper, send_wrapper)
    
    async def _log_transaction(
        self,
        scope: Scope,
        request_body: bytes,
        response_info: Dict[str, Any],
        response_body: bytes,
        process_time: float,
        request_id: str
    ) -> None:
        """Log complete HTTP transaction."""
        try:
            # Create request object for metadata
            request = Request(scope)
            
            # Log request and response
            request_data = self._format_request_data(request, request_body, request_id)
            response_data = self._format_response_data(
                request, response_info, response_body, process_time, request_id
            )
            
            # Choose log level and emoji based on status code
            status_code = response_info.get("status_code", 0)
            if status_code < 400:
                log_level = logging.INFO
                emoji = "🟢" if status_code < 300 else "🟡"
            elif status_code < 500:
                log_level = logging.WARNING
                emoji = "🟠"
            else:
                log_level = logging.ERROR
                emoji = "🔴"
            
            # Log the transaction
            transaction_log = {
                "request": request_data,
                "response": response_data
            }
            
            formatted_json = json.dumps(transaction_log, indent=2, ensure_ascii=False, default=str)
            log_message = f"\n{emoji} HTTP TRANSACTION [{request.method} {request.url.path}]:\n{formatted_json}"
            
            self.logger.log(log_level, log_message)
            
        except Exception as e:
            self.logger.error(f"Error logging HTTP transaction: {e}")
    
    def _format_request_data(self, request: Request, body: bytes, request_id: str) -> Dict[str, Any]:
        """Format request data for logging."""
        # Parse request body
        parsed_body = self._parse_body(body, request.headers.get("content-type", ""))
        
        # Build request info (exclude sensitive headers)
        headers = dict(request.headers)
        if "authorization" in headers:
            headers["authorization"] = "***REDACTED***"
        
        return {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params) if request.query_params else None,
            "headers": headers,
            "client_ip": request.client.host if request.client else None,
            "body": parsed_body
        }
    
    def _format_response_data(
        self,
        request: Request,
        response_info: Dict[str, Any],
        body: bytes,
        process_time: float,
        request_id: str
    ) -> Dict[str, Any]:
        """Format response data for logging."""
        # Parse response headers (ASGI format: list of byte tuples)
        headers = {}
        for header_tuple in response_info.get("headers", []):
            if isinstance(header_tuple, (list, tuple)) and len(header_tuple) >= 2:
                try:
                    name = header_tuple[0].decode('utf-8')
                    value = header_tuple[1].decode('utf-8')
                    headers[name] = value
                except (UnicodeDecodeError, AttributeError):
                    continue
        
        # Parse response body
        content_type = headers.get("content-type", "")
        parsed_body = self._parse_body(body, content_type)
        
        return {
            "request_id": request_id,
            "status_code": response_info.get("status_code", 0),
            "headers": headers,
            "processing_time_ms": round(process_time * 1000, 2),
            "body": parsed_body
        }
    
    def _parse_body(self, body: bytes, content_type: str) -> Any:
        """Parse request/response body based on content type."""
        if not body:
            return None
        
        try:
            if "application/json" in content_type:
                return json.loads(body.decode("utf-8"))
            else:
                # Try to decode as text
                decoded = body.decode("utf-8")
                # Truncate if too long
                if len(decoded) > self.MAX_BODY_SIZE:
                    return f"{decoded[:self.MAX_BODY_SIZE]}... (truncated)"
                return decoded
        except (json.JSONDecodeError, UnicodeDecodeError):
            return f"<Binary data: {len(body)} bytes>"


def create_http_logging_middleware(app: ASGIApp) -> HTTPLoggingMiddleware:
    """Factory function to create HTTP logging middleware."""
    return HTTPLoggingMiddleware(app)