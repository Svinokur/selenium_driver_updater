class Error(Exception):
    """Base class for exceptions in this module."""

class StatusCodeNotEqualException(Error):
    pass

class DriverVersionInvalidException(Error):
    pass
