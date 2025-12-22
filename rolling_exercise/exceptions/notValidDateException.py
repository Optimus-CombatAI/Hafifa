from exceptions.dbIntegrityException import DBIntegrityException


class NotValidDateException(DBIntegrityException):

    def __init__(self):
        message = "Make sure the dates are in the right format"
        super().__init__(message)

    def __str__(self):
        return self.message
