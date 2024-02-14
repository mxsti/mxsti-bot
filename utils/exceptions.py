""" custom exceptions for the discord bot and all helpers """


class SubredditNotFoundOrEmptyError(Exception):
    """
    Custom Exception when a Subreddit is empty or it does not exist

    Attributes:
        subredditname: name of the not existing subreddit
    """

    def __init__(self, subredditname):
        self.subredditname = subredditname
        self.message = f"Subreddit {subredditname} not found or empty"
        super().__init__(self.message)


class TrackmaniaAPIError(Exception):
    """
    Custom Exception when authorization @ trackmania API went wrong

    Attributes:
        message: http error message
        code: http error code
    """

    def __init__(self, message, code):
        self.code = code
        self.message = f"{code}: {message}"
        super().__init__(self.message)
