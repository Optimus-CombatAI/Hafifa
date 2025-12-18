
class NotValidDateException(Exception):

    def __init__(self):
        self.message = "Make sure the dates are in the right format"
        super().__init__(self.message)

    def __str__(self):
        return self.message
