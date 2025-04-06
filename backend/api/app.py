from fastapi import FastAPI
from fastapi import APIRouter

from .router_manager import RouterManager

app = FastAPI()

for router in RouterManager.all().values():
    app.include_router(router)
