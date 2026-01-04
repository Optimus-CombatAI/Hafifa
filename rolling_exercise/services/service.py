from db.pgDatabase import PGDatabase


class Service:
    def __init__(self, db: PGDatabase):
        self.db = db
