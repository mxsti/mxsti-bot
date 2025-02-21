""" custom exceptions for the news helper """


class TagesschauAPIError(Exception):
    """
    Custom Exception when communication with the tagesschau api went wrong

    Attributes:
        message: http error message
        code: http error code
    """

    def __init__(self, message, code):
        self.code = code
        self.message = f"{code}: {message}"
        super().__init__(self.message)
