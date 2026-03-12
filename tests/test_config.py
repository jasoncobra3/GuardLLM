"""
Test suite for GuardConfig

Tests configuration management, validation, and builder patterns.
"""

import pytest
from guardllm.config import GuardConfig, GuardConfigBuilder
from guardllm.exceptions import ConfigurationError


class TestGuardConfigBasic:
    """Test basic GuardConfig functionality"""

    def test_default_config(self) -> None:
        """Test default configuration values"""
        config = GuardConfig()
        assert config.enable_pii_detection is True
        assert config.enable_injection_detection is True
        assert config.enable_audit_logging is False
        assert config.custom_pii_patterns == {}
        assert config.custom_scoring_weights == {}
        assert config.redact_sensitive_data is True

    def test_custom_config(self) -> None:
        """Test custom configuration"""
        config = GuardConfig(
            enable_pii_detection=False,
            enable_audit_logging=True,
            log_file_path="/tmp/audit.log"
        )
        assert config.enable_pii_detection is False
        assert config.enable_audit_logging is True
        assert config.log_file_path == "/tmp/audit.log"

    def test_with_patterns(self) -> None:
        """Test config with custom patterns"""
        config = GuardConfig(
            custom_pii_patterns={"employee_id": r"EMP\d{6}"},
            custom_scoring_weights={"injection": 0.8}
        )
        assert "employee_id" in config.custom_pii_patterns
        assert config.custom_scoring_weights["injection"] == 0.8


class TestConfigValidation:
    """Test configuration validation"""

    def test_valid_config(self) -> None:
        """Test validation of valid config"""
        config = GuardConfig()
        config.validate()  # Should not raise

    def test_invalid_boolean_field(self) -> None:
        """Test validation of invalid boolean field"""
        config = GuardConfig()
        config.enable_pii_detection = "yes"  # Should be boolean
        with pytest.raises(ValueError):
            config.validate()

    def test_negative_weight(self) -> None:
        """Test validation rejects negative weights"""
        config = GuardConfig(custom_scoring_weights={"test": -0.5})
        with pytest.raises(ValueError):
            config.validate()

    def test_invalid_weight_type(self) -> None:
        """Test validation rejects non-numeric weights"""
        config = GuardConfig(custom_scoring_weights={"test": "high"})
        with pytest.raises(ValueError):
            config.validate()

    def test_zero_weight(self) -> None:
        """Test that zero weights are valid"""
        config = GuardConfig(custom_scoring_weights={"test": 0.0})
        config.validate()  # Should not raise

    def test_high_weight(self) -> None:
        """Test that high weights are valid"""
        config = GuardConfig(custom_scoring_weights={"test": 5.0})
        config.validate()  # Should not raise


class TestConfigSerialization:
    """Test configuration serialization"""

    def test_to_dict(self) -> None:
        """Test converting config to dictionary"""
        config = GuardConfig(
            enable_pii_detection=False,
            log_file_path="/var/log/audit.log",
            custom_scoring_weights={"custom": 0.5}
        )
        config_dict = config.to_dict()

        assert config_dict["enable_pii_detection"] is False
        assert config_dict["log_file_path"] == "/var/log/audit.log"
        assert config_dict["custom_scoring_weights"]["custom"] == 0.5

    def test_from_dict(self) -> None:
        """Test creating config from dictionary"""
        config_dict = {
            "enable_pii_detection": False,
            "enable_injection_detection": True,
            "log_file_path": "/tmp/test.log",
            "custom_scoring_weights": {"test": 0.5}
        }
        config = GuardConfig.from_dict(config_dict)

        assert config.enable_pii_detection is False
        assert config.log_file_path == "/tmp/test.log"
        assert config.custom_scoring_weights["test"] == 0.5

    def test_from_dict_validation(self) -> None:
        """Test that from_dict validates configuration"""
        config_dict = {
            "enable_pii_detection": True,
            "custom_scoring_weights": {"invalid": -1.0}
        }
        with pytest.raises(ValueError):
            GuardConfig.from_dict(config_dict)

    def test_roundtrip_serialization(self) -> None:
        """Test roundtrip: config -> dict -> config"""
        original = GuardConfig(
            enable_pii_detection=False,
            enable_audit_logging=True,
            log_file_path="/var/log/test.log",
            custom_scoring_weights={"a": 0.5, "b": 0.3}
        )

        config_dict = original.to_dict()
        restored = GuardConfig.from_dict(config_dict)

        assert restored.enable_pii_detection == original.enable_pii_detection
        assert restored.log_file_path == original.log_file_path
        assert restored.custom_scoring_weights == original.custom_scoring_weights


class TestGuardConfigBuilder:
    """Test GuardConfigBuilder fluent API"""

    def test_builder_basic(self) -> None:
        """Test basic builder usage"""
        config = (GuardConfigBuilder()
                  .with_pii_detection(False)
                  .with_injection_detection(True)
                  .build())

        assert config.enable_pii_detection is False
        assert config.enable_injection_detection is True

    def test_builder_with_logging(self) -> None:
        """Test builder with logging configuration"""
        config = (GuardConfigBuilder()
                  .with_audit_logging(True)
                  .with_log_file("/var/log/audit.log")
                  .with_log_to_console(False)
                  .build())

        assert config.enable_audit_logging is True
        assert config.log_file_path == "/var/log/audit.log"
        assert config.log_to_console is False

    def test_builder_with_custom_patterns(self) -> None:
        """Test builder with custom patterns"""
        config = (GuardConfigBuilder()
                  .with_custom_pii_pattern("employee_id", r"EMP\d{6}")
                  .with_custom_pii_pattern("department", r"DEPT\d{3}")
                  .build())

        assert len(config.custom_pii_patterns) == 2
        assert config.custom_pii_patterns["employee_id"] == r"EMP\d{6}"

    def test_builder_with_weights(self) -> None:
        """Test builder with scoring weights"""
        config = (GuardConfigBuilder()
                  .with_custom_scoring_weight("critical_threat", 0.9)
                  .with_custom_scoring_weight("warning", 0.3)
                  .build())

        assert config.custom_scoring_weights["critical_threat"] == 0.9
        assert config.custom_scoring_weights["warning"] == 0.3

    def test_builder_chaining(self) -> None:
        """Test method chaining"""
        config = (GuardConfigBuilder()
                  .with_pii_detection(True)
                  .with_injection_detection(True)
                  .with_audit_logging(True)
                  .with_log_file("/var/log/guard.log")
                  .with_sensitive_data_redaction(True)
                  .with_custom_pii_pattern("ssn", r"\d{3}-\d{2}-\d{4}")
                  .with_custom_scoring_weight("injection", 0.8)
                  .build())

        assert config.enable_pii_detection is True
        assert config.enable_injection_detection is True
        assert config.enable_audit_logging is True
        assert config.log_file_path == "/var/log/guard.log"
        assert config.redact_sensitive_data is True

    def test_builder_validation_on_build(self) -> None:
        """Test that builder validates on build()"""
        builder = GuardConfigBuilder()
        builder._config.custom_scoring_weights["invalid"] = -0.5

        with pytest.raises(ValueError):
            builder.build()

    def test_builder_redaction_setting(self) -> None:
        """Test builder redaction setting"""
        config = (GuardConfigBuilder()
                  .with_sensitive_data_redaction(False)
                  .build())

        assert config.redact_sensitive_data is False


class TestConfigEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_custom_patterns(self) -> None:
        """Test config with empty custom patterns"""
        config = GuardConfig(custom_pii_patterns={})
        config.validate()  # Should not raise

    def test_none_log_file(self) -> None:
        """Test config with None log file"""
        config = GuardConfig(log_file_path=None)
        config.validate()  # Should not raise

    def test_multiple_weights(self) -> None:
        """Test config with many weights"""
        weights = {f"issue_{i}": 0.1 * i for i in range(1, 11)}
        config = GuardConfig(custom_scoring_weights=weights)
        config.validate()  # Should not raise
        assert len(config.custom_scoring_weights) == 10

    def test_very_high_weight(self) -> None:
        """Test very high weight values"""
        config = GuardConfig(custom_scoring_weights={"extreme": 1000.0})
        config.validate()  # Should not raise

    def test_very_small_weight(self) -> None:
        """Test very small weight values"""
        config = GuardConfig(custom_scoring_weights={"tiny": 0.00001})
        config.validate()  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
