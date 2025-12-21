
class ConnectionException(Exception):

    def __init__(self):
        self.message = f"There has been a connection error"
        super().__init__(self.message)

    def __str__(self):
        return self.message
