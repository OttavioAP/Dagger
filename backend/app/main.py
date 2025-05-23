from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.logger import logger
from app.api.user import router as user_router
from app.api.tasks import router as tasks_router
from app.api.teams import router as teams_router
from app.api.dag import router as dags_router
from app.api.user_tasks import router as user_tasks_router
from app.api.week import router as weeks_router
from app.api.agentic import router as agentic_router

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


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_config=logger,  # type: ignore
        log_level="info",
        access_log=True,
    )
