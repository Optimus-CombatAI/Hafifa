
class NotExistingCityException(Exception):

    def __init__(self):
        self.message = "The city doesn't exist"
        super().__init__(self.message)

    def __str__(self):
        return self.message
