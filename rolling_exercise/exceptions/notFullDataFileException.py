from exceptions.dbIntegrityException import DBIntegrityException


class NotFullDataFileException(DBIntegrityException):

    def __init__(self):
        message = "Make sure the file is full and there are no empty cells"
        super().__init__(message)

    def __str__(self):
        return self.message
