"""
GuardLLM Exception Classes

Defines custom exceptions for GuardLLM with clear error messaging.
"""


class GuardLLMException(Exception):
    """
    Base exception class for all GuardLLM errors.

    All GuardLLM-specific exceptions inherit from this class.

    Example:
        >>> try:
        ...     # GuardLLM operation
        ...     pass
        ... except GuardLLMException as e:
        ...     print(f"GuardLLM error: {e}")
    """

    pass


class ConfigurationError(GuardLLMException):
    """
    Raised when there's an error in Guard configuration.

    This exception is raised when invalid configuration values are provided
    or configuration validation fails.

    Example:
        >>> from guardllm import Guard
        >>> from guardllm.config import GuardConfig
        >>> config = GuardConfig(custom_scoring_weights={"invalid": -0.5})
        >>> try:
        ...     config.validate()
        ... except ConfigurationError as e:
        ...     print(f"Config error: {e}")
    """

    pass


class DetectionError(GuardLLMException):
    """
    Raised when a detection process encounters an error.

    This exception is raised when a detector fails during scanning or
    if invalid input is provided to detectors.

    Example:
        >>> from guardllm.safety.pii_detector import PIIDetector
        >>> detector = PIIDetector()
        >>> try:
        ...     detector.add_custom_pattern("test", "[invalid(")  # Invalid regex
        ... except DetectionError as e:
        ...     print(f"Detection error: {e}")
    """

    pass


class LoggingError(GuardLLMException):
    """
    Raised when audit logging fails.

    This exception is raised when the AuditLogger fails to write logs,
    initialize, or export logs.

    Example:
        >>> from guardllm.observability import AuditLogger
        >>> try:
        ...     logger = AuditLogger(log_file_path="/invalid/path/file.log")
        ... except LoggingError as e:
        ...     print(f"Logging error: {e}")
    """

    pass


class ScanError(GuardLLMException):
    """
    Raised when a scan operation fails.

    This exception is raised when Guard.scan() encounters an unrecoverable error.

    Example:
        >>> from guardllm import Guard
        >>> guard = Guard()
        >>> try:
        ...     report = guard.scan("test")  # May raise ScanError in edge cases
        ... except ScanError as e:
        ...     print(f"Scan error: {e}")
    """

    pass


class PatternError(DetectionError):
    """
    Raised when there's an error with regex pattern handling.

    This exception is raised when pattern compilation or usage fails.
    It's a subclass of DetectionError for more specific error handling.

    Example:
        >>> from guardllm.safety.pii_detector import PIIDetector
        >>> detector = PIIDetector()
        >>> try:
        ...     detector.add_custom_pattern("invalid", "[invalid(")
        ... except PatternError as e:
        ...     print(f"Pattern error: {e}")
    """

    pass


class ValidationError(GuardLLMException):
    """
    Raised when data validation fails.

    This exception is raised when required data fails validation checks.

    Example:
        >>> from guardllm.core import GuardReport
        >>> try:
        ...     report = GuardReport(
        ...         prompt="test",
        ...         risk_score=1.5  # Invalid: > 1.0
        ...     )
        ... except ValidationError as e:
        ...     print(f"Validation error: {e}")
    """

    pass
