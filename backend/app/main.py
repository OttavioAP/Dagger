from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.logger import logger


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
