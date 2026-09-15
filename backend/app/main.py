from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.properties import router as properties_router
from app.core.config import settings
from app.api.routes.auth import router as auth_router
from app.api.routes.buildings import router as buildings_router
from app.api.routes.units import router as units_router
from app.api.routes.leases import router as leases_router
from app.api.routes.tenants import router as tenants_router
from app.api.routes.expenses import router as expenses_router
from app.api.routes.rent_obligations import router as rent_obligations_router


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

app.include_router(
    buildings_router,
    prefix="/api",
    tags=["Buildings"],
)

app.include_router(
    units_router,
    prefix="/api",
    tags=["Units"],
)

app.include_router(
    tenants_router,
    prefix="/api/tenants",
    tags=["Tenants"],
)

app.include_router(
    leases_router,
    prefix="/api",
    tags=["Leases"],
)

app.include_router(
    expenses_router,
    prefix="/api",
    tags=["Expenses"],
)

app.include_router(
    rent_obligations_router,
    prefix="/api",
    tags=["Rent Obligations"],
)