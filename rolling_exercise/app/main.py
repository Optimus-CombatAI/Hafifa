from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.session import Base, engine
from app.db import models
from app.routes.router import api_router  


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(title="Air Quality API", lifespan=lifespan)

app.include_router(api_router) 

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
