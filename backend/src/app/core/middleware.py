import json
import time
import logging
import uuid
from contextvars import ContextVar
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone

# Context Variable to store correlation ID thread-safely across async tasks
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")
user_id_ctx: ContextVar[str] = ContextVar("user_id", default="ANONYMOUS")

class StructuredJSONFormatter(logging.Formatter):
    """Custom JSON log formatter to capture enterprise telemetry tracking tokens dynamically."""
    def format(self, record: logging.LogRecord) -> str:
        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "bench-sales-engine",
            "module": record.module,
            "message": record.getMessage(),
            "correlation_id": correlation_id_ctx.get(),
            "user_id": user_id_ctx.get()
        }
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_payload)

class TelemetryPerimeterMiddleware(BaseHTTPMiddleware):
    """
    FastAPI Core Middleware managing trace propagation, lifecycle correlation metrics,
    and structured JSON log ledger extraction blocks at the system edge.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        
        # 1. Capture or extract external correlation headers safely
        incoming_corr_id = request.headers.get("X-Correlation-ID")
        correlation_token = incoming_corr_id if incoming_corr_id else str(uuid.uuid4())
        
        # Set context variables thread-safely
        corr_token_str = correlation_id_ctx.set(correlation_token)
        
        # 2. Setup standard request tracking tags
        request_id = str(uuid.uuid4())
        
        # Extract user identification safely if token parsing occurred earlier
        user_token = "ANONYMOUS"
        if hasattr(request.state, "user") and request.state.user:
            user_token = str(request.state.user.id)
        user_token_str = user_id_ctx.set(user_token)

        logger = logging.getLogger("app.telemetry")
        logger.info(f"Inbound HTTP Request Intercepted: {request.method} {request.url.path}")

        try:
            response = await call_next(request)
            
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            response.headers["X-Correlation-ID"] = correlation_token
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            logger.info(
                f"Outbound HTTP Response Context Dispatched",
                extra={
                    "route": request.url.path,
                    "method": request.method,
                    "status": response.status_code,
                    "duration_ms": duration_ms,
                    "request_id": request_id
                }
            )
            return response
            
        except Exception as error:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.error(
                f"Unhandled Exception Caught at Perimeter Boundary: {str(error)}",
                exc_info=True,
                extra={
                    "route": request.url.path,
                    "method": request.method,
                    "status": 500,
                    "duration_ms": duration_ms,
                    "request_id": request_id
                }
            )
            raise error
        finally:
            # Clean context blocks securely to prevent memory contamination leaks
            correlation_id_ctx.reset(corr_token_str)
            user_id_ctx.reset(user_token_str)