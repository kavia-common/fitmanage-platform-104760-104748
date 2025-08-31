from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.api.router import api_router
from src.core.config import get_settings
from src.core.dependencies import setup_cors


def create_app() -> FastAPI:
    """Create and configure the FastAPI app instance with routers and middleware."""
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        contact={"name": "API Support"},
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )

    # Middleware
    setup_cors(app)

    # Root health check
    @app.get("/", summary="Health Check", tags=["health"])
    def health_check():
        return JSONResponse({"message": "Healthy", "env": settings.ENV})

    # Include API router under /api
    app.include_router(api_router, prefix="/api")

    return app


# PUBLIC_INTERFACE
app = create_app()
