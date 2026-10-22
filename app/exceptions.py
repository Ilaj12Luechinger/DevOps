class ValidationError(ValueError):
    """Raised when client input does not satisfy the Task invariants."""


class NotFoundError(ValueError):
    """Raised when a user wants to update an object that does not exist"""
