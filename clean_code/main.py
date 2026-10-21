from app import MusicPlayerApp
from logging_config import configure_logging


def main():
    configure_logging()

    app = MusicPlayerApp()
    app.run()


if __name__ == "__main__":
    main()
