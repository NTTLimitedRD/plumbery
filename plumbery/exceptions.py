class PlumberyException(Exception):
    def __init__(self, message):
        self.message = message
        super(PlumberyException, message).__init__(message)
