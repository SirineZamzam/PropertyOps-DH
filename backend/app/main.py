from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.properties import router as properties_router
from app.core.config import settings
from app.api.routes.auth import router as auth_router


app = FastAPI(
    title=settings.app_name,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
    }


app.include_router(
    properties_router,
    prefix="/api/properties",
    tags=["Properties"],
)

app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"],
)