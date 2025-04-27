from fastapi import FastAPI
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.settings.web import WebSettings
from backend import __version__

from .router_manager import RouterManager
from .security import SessionMiddleware

web_settings: WebSettings = WebSettings() #type: ignore

app = FastAPI(
    title=web_settings.WEB_TITLE,
    version=__version__,
)

for router in RouterManager.all().values():
    app.include_router(router)

app.add_middleware(SessionMiddleware)

# Exceptions handlers --------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom HTTP exception handler.
    """
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
    
    if response.status_code == 401:
        response.delete_cookie("session")
        response.delete_cookie("profile")
    
    return response
