""" custom exceptions for the youtube download helper """


class DownloadFailedError(Exception):
    """
    Custom Exception when downloading video from youtube went wrong

    Attributes:
        message: error message
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
