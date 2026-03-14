"""
GuardConfig: Configuration system for Guard

Provides configuration classes and settings for customizing Guard behavior.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class GuardConfig:
    """
    Configuration for Guard instance.

    Allows customization of Guard behavior including which detectors to enable,
    custom weights, logging configuration, and data sensitivity settings.

    Attributes:
        enable_pii_detection: Enable PII detection
        enable_injection_detection: Enable prompt injection detection
        enable_audit_logging: Enable audit logging
        custom_pii_patterns: Custom regex patterns for PII detection
        custom_scoring_weights: Custom risk scoring weights
        log_file_path: Path to audit log file
        log_to_console: Whether to log to console
        log_to_file: Whether to log to file
        redact_sensitive_data: Whether to mask PII in logs
    """

    enable_pii_detection: bool = True
    enable_injection_detection: bool = True
    enable_audit_logging: bool = False

    custom_pii_patterns: Dict[str, str] = field(default_factory=dict)
    custom_scoring_weights: Dict[str, float] = field(default_factory=dict)

    log_file_path: Optional[str] = None
    log_to_console: bool = True
    log_to_file: bool = True
    redact_sensitive_data: bool = True

    def validate(self) -> None:
        """
        Validate configuration settings.

        Raises:
            ValueError: If any configuration value is invalid

        Example:
            >>> config = GuardConfig()
            >>> config.validate()  # Passes
        """
        if not isinstance(self.enable_pii_detection, bool):
            raise ValueError("enable_pii_detection must be boolean")

        if not isinstance(self.enable_injection_detection, bool):
            raise ValueError("enable_injection_detection must be boolean")

        if not isinstance(self.enable_audit_logging, bool):
            raise ValueError("enable_audit_logging must be boolean")

        if not isinstance(self.custom_pii_patterns, dict):
            raise ValueError("custom_pii_patterns must be dictionary")

        if not isinstance(self.custom_scoring_weights, dict):
            raise ValueError("custom_scoring_weights must be dictionary")

        # Validate weight values
        for weight_name, weight_value in self.custom_scoring_weights.items():
            if not isinstance(weight_value, (int, float)):
                raise ValueError(
                    f"Weight '{weight_name}' must be numeric, got {type(weight_value)}"
                )
            if weight_value < 0:
                raise ValueError(f"Weight '{weight_name}' must be non-negative")

        if self.log_file_path and not isinstance(self.log_file_path, str):
            raise ValueError("log_file_path must be string or None")

    def to_dict(self) -> Dict:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration

        Example:
            >>> config = GuardConfig()
            >>> config_dict = config.to_dict()
        """
        return {
            "enable_pii_detection": self.enable_pii_detection,
            "enable_injection_detection": self.enable_injection_detection,
            "enable_audit_logging": self.enable_audit_logging,
            "custom_pii_patterns": self.custom_pii_patterns,
            "custom_scoring_weights": self.custom_scoring_weights,
            "log_file_path": self.log_file_path,
            "log_to_console": self.log_to_console,
            "log_to_file": self.log_to_file,
            "redact_sensitive_data": self.redact_sensitive_data,
        }

    @staticmethod
    def from_dict(config_dict: Dict) -> "GuardConfig":
        """
        Create configuration from dictionary.

        Args:
            config_dict: Dictionary containing configuration values

        Returns:
            GuardConfig instance

        Raises:
            ValueError: If required keys are missing or values are invalid

        Example:
            >>> config_dict = {
            ...     "enable_pii_detection": True,
            ...     "enable_injection_detection": True,
            ... }
            >>> config = GuardConfig.from_dict(config_dict)
        """
        try:
            config = GuardConfig(**config_dict)
            config.validate()
            return config
        except TypeError as e:
            raise ValueError(f"Invalid configuration: {e}")


class GuardConfigBuilder:
    """
    Builder class for fluent GuardConfig construction.

    Allows easy building of GuardConfig with method chaining.

    Example:
        >>> config = (GuardConfigBuilder()
        ...     .with_pii_detection(True)
        ...     .with_injection_detection(True)
        ...     .with_audit_logging(True)
        ...     .with_log_file("audit.log")
        ...     .build())
    """

    def __init__(self) -> None:
        """Initialize builder with default config."""
        self._config = GuardConfig()

    def with_pii_detection(self, enabled: bool) -> "GuardConfigBuilder":
        """Enable or disable PII detection."""
        self._config.enable_pii_detection = enabled
        return self

    def with_injection_detection(self, enabled: bool) -> "GuardConfigBuilder":
        """Enable or disable prompt injection detection."""
        self._config.enable_injection_detection = enabled
        return self

    def with_audit_logging(self, enabled: bool) -> "GuardConfigBuilder":
        """Enable or disable audit logging."""
        self._config.enable_audit_logging = enabled
        return self

    def with_log_file(self, file_path: Optional[str]) -> "GuardConfigBuilder":
        """Set audit log file path."""
        self._config.log_file_path = file_path
        return self

    def with_log_to_console(self, enabled: bool) -> "GuardConfigBuilder":
        """Enable or disable console logging."""
        self._config.log_to_console = enabled
        return self

    def with_sensitive_data_redaction(self, enabled: bool) -> "GuardConfigBuilder":
        """Enable or disable sensitive data redaction in logs."""
        self._config.redact_sensitive_data = enabled
        return self

    def with_custom_pii_pattern(self, name: str, pattern: str) -> "GuardConfigBuilder":
        """Add custom PII detection pattern."""
        self._config.custom_pii_patterns[name] = pattern
        return self

    def with_custom_scoring_weight(self, issue_type: str, weight: float) -> "GuardConfigBuilder":
        """Set custom risk scoring weight."""
        self._config.custom_scoring_weights[issue_type] = weight
        return self

    def build(self) -> GuardConfig:
        """
        Build and validate the configuration.

        Returns:
            Validated GuardConfig instance

        Raises:
            ValueError: If configuration is invalid
        """
        self._config.validate()
        return self._config
