from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.openapi.utils import get_openapi
from pathlib import Path
import json
from pydantic import BaseModel
import inspect
import importlib
import pkgutil

from app.core.logger import logger
from app.api.user import router as user_router
from app.api.tasks import router as tasks_router
from app.api.teams import router as teams_router
from app.api.dag import router as dags_router
from app.api.user_tasks import router as user_tasks_router
from app.api.week import router as weeks_router
from app.api.agentic import router as agentic_router
from app.services.scheduler_service import scheduler_service

app = FastAPI(
    title="Dagger API",
    description="API for Dagger AI application",
    version="0.0.1",
    logger=logger,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000/",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(tasks_router)
app.include_router(teams_router)
app.include_router(dags_router)
app.include_router(user_tasks_router)
app.include_router(weeks_router)
app.include_router(agentic_router)


@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the application starts."""
    scheduler_service.start()
    logger.info("Application started")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the scheduler when the application shuts down."""
    scheduler_service.stop()
    logger.info("Application shutdown")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# @app.on_event("startup")
# async def export_schemas():
#     """Export OpenAPI schema and all Pydantic model schemas on startup."""
#     try:
#         schema_dir = Path(__file__).parent.parent / "schemas"
#         schema_dir.mkdir(parents=True, exist_ok=True)

#         # 1. Export OpenAPI schema
#         openapi_schema = get_openapi(
#             title=app.title,
#             version=app.version,
#             routes=app.routes,
#             description=app.description
#         )
#         with open(schema_dir / "openapi.json", "w") as f:
#             json.dump(openapi_schema, f, indent=2)
#         logger.info("Exported OpenAPI schema")

#         # 2. Export all Pydantic model schemas in app.schema
#         def discover_models(package_name: str):
#             package = importlib.import_module(package_name)
#             for _, modname, _ in pkgutil.walk_packages(package.__path__, prefix=package.__name__ + "."):
#                 module = importlib.import_module(modname)
#                 for name, obj in inspect.getmembers(module):
#                     if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel:
#                         yield obj

#         for model in discover_models("app.schema"):
#             with open(schema_dir / f"{model.__name__}.json", "w") as f:
#                 json.dump(model.model_json_schema(), f, indent=2)
#             logger.info(f"Exported schema for {model.__name__}")

#     except Exception as e:
#         logger.error(f"Error exporting schemas: {str(e)}")
#         raise e

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_config=logger,  # type: ignore
        log_level="info",
        access_log=True,
    )
