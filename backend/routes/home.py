"""Root status endpoint for verifying backend health.

Exposes a simple GET "/" route that returns an HTML message indicating the
backend is running and instructing the user to open the frontend URL.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/")
async def get_status():
    """Return a simple HTML health/status message for the backend."""
    return HTMLResponse(
        content="<h3>Your backend is running correctly. Please open the front-end URL (default is http://localhost:5173) to use screenshot-to-code.</h3>"
    )
