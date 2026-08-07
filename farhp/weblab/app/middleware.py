from __future__ import annotations
import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, hsts_seconds: int = 0, csp_report_only: bool = False):
        super().__init__(app)
        self.hsts_seconds = hsts_seconds
        self.csp_header = "Content-Security-Policy-Report-Only" if csp_report_only else "Content-Security-Policy"

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=()")
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        response.headers.setdefault(
            self.csp_header,
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "media-src 'self' blob: data:; connect-src 'self'; worker-src 'self' blob:; "
            "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'",
        )
        if self.hsts_seconds > 0 and request.url.scheme == "https":
            response.headers.setdefault("Strict-Transport-Security", f"max-age={self.hsts_seconds}; includeSubDomains")
        request_id = request.headers.get("X-Request-ID") or secrets.token_hex(12)
        response.headers.setdefault("X-Request-ID", request_id)
        if request.url.path.startswith("/api/"):
            response.headers.setdefault("Cache-Control", "no-store")
        return response
