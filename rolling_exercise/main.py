import uvicorn

from src.api.app import create_app
from src.configs.logging_config import configure_logging
from src.configs.settings import ApiSettings

settings = ApiSettings()
configure_logging(settings.log_file_path)

app = create_app(settings)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.api_host, port=settings.api_port, log_config=None)
