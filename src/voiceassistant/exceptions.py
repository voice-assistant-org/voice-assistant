"""Host custom exceptions."""


class AssistantBaseException(Exception):
    """Base assistant exception."""


class ConfigValidationError(AssistantBaseException):
    """Config Validation Error."""


class NlpException(AssistantBaseException):
    """Natural Language Processor Error."""


class SetupIncomplete(AssistantBaseException):
    """Setup Incomplete Exception."""
