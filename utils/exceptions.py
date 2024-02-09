""" custom exceptions for the discord bot and all helpers """


class SubredditNotFoundOrEmptyError(Exception):
    """
    Custom Exception when a Subreddit is empty or it does not exist

    Attributes:
        subredditname: name of the not existing subreddit
        message: explanation of the error
    """

    def __init__(self, subredditname, message="Subreddit not found or empty"):
        self.subredditname = subredditname
        self.message = message
        super().__init__(self.message)