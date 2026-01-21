"""Root status endpoint for verifying backend health.

Exposes a simple GET "/" route that returns an HTML message indicating the
backend is running and instructing the user to open the frontend URL.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/")
async def get_status():
    """
    Provide an HTML status page indicating the backend is running.
    
    The response contains a short HTML message instructing the user to open the front-end URL (default http://localhost:5173) to use the application.
    
    Returns:
        HTMLResponse: An HTML response containing the status message.
    """
    return HTMLResponse(
        content="<h3>Your backend is running correctly. Please open the front-end URL (default is http://localhost:5173) to use screenshot-to-code.</h3>"
    )