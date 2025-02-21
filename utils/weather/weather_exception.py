""" custom exceptions for the weather helper """

class WeatherAPIError(Exception):
    """
    Custom Exception when communication with the tommorow weather api went wrong

    Attributes:
        message: http error message
        code: http error code
    """

    def __init__(self, message, code):
        self.code = code
        self.message = f"{code}: {message}"
        super().__init__(self.message)
