"""
Custom exceptions for Text-to-SQL Assistant
"""

class Text2SQLError(Exception):
    """Base exception for Text-to-SQL Assistant"""
    pass

class ModelLoadError(Text2SQLError):
    """Raised when model loading fails"""
    pass

class DatabaseConnectionError(Text2SQLError):
    """Raised when database connection fails"""
    pass

class SQLGenerationError(Text2SQLError):
    """Raised when SQL generation fails"""
    pass

class SQLSafetyError(Text2SQLError):
    """Raised when SQL fails safety checks"""
    pass

class ConfigurationError(Text2SQLError):
    """Raised when configuration is invalid"""
    pass

class TimeoutError(Text2SQLError):
    """Raised when operation times out"""
    pass
