import uvicorn
from fastapi import FastAPI

from src.api import health_router
from src.configs.logging_config import configure_logging
from src.configs.settings import ApiSettings

settings = ApiSettings()
configure_logging(settings.log_file_path)

app = FastAPI(title="Air Quality API")
app.include_router(health_router.router)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.api_host, port=settings.api_port, log_config=None)
