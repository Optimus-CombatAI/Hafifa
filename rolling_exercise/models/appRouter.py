from typing import List, Type

from fastapi import APIRouter

from db.database import Database
from models.service import Service


class AppRouter(APIRouter):
    def __init__(self, prefix: str, tags: List[str], db: Database, service_class: Type[Service]):
        super().__init__(prefix=prefix, tags=tags)
        self.db = db
        self.service = service_class(db)
