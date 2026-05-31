class PizzaNotFound(Exception):
    """Raised when a pizza is not found by ID."""
    pass


class DuplicatePizzaName(Exception):
    """Raised when attempting to create a pizza with a name that already exists."""

    pass


class InvalidCredentials(Exception):
    """Raised when email or password is incorrect. Same type for both to prevent enumeration."""

    pass
