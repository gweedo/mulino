class PizzaNotFound(Exception):
    """Raised when a pizza is not found by ID."""
    pass


class DuplicatePizzaName(Exception):
    """Raised when attempting to create a pizza with a name that already exists."""
    pass
