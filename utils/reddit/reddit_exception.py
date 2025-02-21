""" custom exceptions for the reddit helper """

class SubredditNotFoundOrEmptyError(Exception):
    """
    Custom Exception when a Subreddit is empty or it does not exist

    Attributes:
        subredditname: name of the not existing subreddit
        message: explanation of the error
    """

    def __init__(self, subredditname):
        self.subredditname = subredditname
        self.message = f"Subreddit {subredditname} not found or empty"
        super().__init__(self.message)
