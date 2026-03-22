from fastapi import APIRouter
from .endpoints import photo

api_router = APIRouter()
api_router.include_router(photo.router, prefix="/photo", tags=["photo"])
