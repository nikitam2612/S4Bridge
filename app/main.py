from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.endpoints.customers import (
    router as customer_router,
)
from app.api.v1.endpoints.integrations import (
    router as integration_router,
)
from app.api.v1.endpoints.inventory import (
    router as inventory_router,
)
from app.api.v1.endpoints.products import (
    router as product_router,
)
from app.api.v1.endpoints.sales_orders import (
    router as sales_order_router,
)
from app.db.init_db import close_databases, initialize_databases


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_databases()

    print("PostgreSQL connected successfully")
    print("MongoDB connected successfully")
    print("MongoDB indexes initialized successfully")

    yield

    close_databases()
    print("Database connections closed")


app = FastAPI(
    title="S4Bridge API",
    description=("Enterprise SAP Integration and Order Management Platform"),
    version="1.0.0",
    lifespan=lifespan,
)


# API Routers

app.include_router(
    integration_router,
    prefix="/api/v1",
)

app.include_router(
    customer_router,
    prefix="/api/v1",
)

app.include_router(
    product_router,
    prefix="/api/v1",
)

app.include_router(
    inventory_router,
    prefix="/api/v1",
)

app.include_router(
    sales_order_router,
    prefix="/api/v1",
)


# Health Endpoints


@app.get("/", tags=["Health"])
def root():
    return {
        "application": "S4Bridge",
        "message": "Enterprise Integration Platform is running",
        "version": "1.0.0",
        "status": "healthy",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "S4Bridge API",
    }
