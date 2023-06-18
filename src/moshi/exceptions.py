class AuthenticationError(Exception):
    """Raised when backend authentication fails."""
    ...

class UserResetError(Exception):
    """Raised when something unexpected happens and the user should reload the page."""
    ...
