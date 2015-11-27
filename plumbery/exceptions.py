class PlumberyException(Exception):
    def __init__(self, message):
        self.message = message
        super(PlumberyException, self).__init__(message)
