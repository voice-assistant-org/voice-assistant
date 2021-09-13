"""Host custom exceptions."""


class AssistantBaseException(Exception):
    """Base assistant exception."""


class ConfigValidationError(AssistantBaseException):
    """Config Validation Error."""


class SkillError(AssistantBaseException):
    """Skill Error."""


class ActionError(AssistantBaseException):
    """Action Error."""


class IntegrationError(AssistantBaseException):
    """Integration Error."""


class NlpException(AssistantBaseException):
    """Natural Language Processor Error."""


class SetupIncomplete(AssistantBaseException):
    """Setup Incomplete Exception."""


class DottedAttribureError(AttributeError, AssistantBaseException):
    """Dotted Dictionary Attribute Error."""
