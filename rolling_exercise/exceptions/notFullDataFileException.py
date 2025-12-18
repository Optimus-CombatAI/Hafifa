
class NotFullDataFileException(Exception):

    def __init__(self):
        self.message = "Make sure the file is full and there are no empty cells"
        super().__init__(self.message)

    def __str__(self):
        return self.message
