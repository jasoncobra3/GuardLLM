"""
Test suite for PIIDetector

Tests PII pattern recognition and detection functionality across all
supported PII types.
"""

import pytest
from guardllm.safety.pii_detector import PIIDetector


class TestPIIDetectorBasic:
    """Test basic PII detection functionality"""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        """Create a fresh PIIDetector instance for each test"""
        return PIIDetector()

    def test_email_detection(self, detector: PIIDetector) -> None:
        """Test email address detection"""
        result = detector.detect("Contact me at john.doe@example.com")
        assert "email" in result
        assert "john.doe@example.com" in result["email"]

    def test_email_multiple(self, detector: PIIDetector) -> None:
        """Test detection of multiple email addresses"""
        result = detector.detect("Email alice@example.com or bob@test.org for help")
        assert "email" in result
        assert len(result["email"]) == 2

    def test_phone_us_detection(self, detector: PIIDetector) -> None:
        """Test US phone number detection"""
        result = detector.detect("Call me at 555-123-4567")
        assert "phone_us" in result or "phone_international" in result

    def test_ssn_detection(self, detector: PIIDetector) -> None:
        """Test Social Security Number detection"""
        result = detector.detect("My SSN is 123-45-6789")
        assert "ssn" in result
        assert "123-45-6789" in result["ssn"]

    def test_credit_card_visa(self, detector: PIIDetector) -> None:
        """Test Visa credit card detection"""
        result = detector.detect("Card: 4532015112830366")
        assert "credit_card_visa" in result

    def test_credit_card_mastercard(self, detector: PIIDetector) -> None:
        """Test Mastercard detection"""
        result = detector.detect("5425233010103442")
        assert "credit_card_mastercard" in result

    def test_credit_card_amex(self, detector: PIIDetector) -> None:
        """Test American Express detection"""
        result = detector.detect("Amex: 378282246310005")
        assert "credit_card_amex" in result

    def test_ipv4_detection(self, detector: PIIDetector) -> None:
        """Test IPv4 address detection"""
        result = detector.detect("Connect to 192.168.1.1 for admin")
        assert "ipv4" in result
        assert "192.168.1.1" in result["ipv4"]

    def test_api_key_detection(self, detector: PIIDetector) -> None:
        """Test API key detection"""
        result = detector.detect("api_key = 'sk_live_51234567890abcdefghij'")
        assert "api_key" in result

    def test_no_pii(self, detector: PIIDetector) -> None:
        """Test text with no PII"""
        result = detector.detect("Hello, this is a normal sentence with no sensitive data.")
        assert len(result) == 0


class TestPIIDetectorHasPII:
    """Test has_pii quick boolean check"""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        return PIIDetector()

    def test_has_pii_true(self, detector: PIIDetector) -> None:
        """Test has_pii returns True when PII is present"""
        assert detector.has_pii("john@example.com") is True

    def test_has_pii_false(self, detector: PIIDetector) -> None:
        """Test has_pii returns False when no PII present"""
        assert detector.has_pii("Hello world") is False

    def test_has_pii_multiple_types(self, detector: PIIDetector) -> None:
        """Test has_pii with multiple PII types"""
        text = "Email john@example.com, SSN 123-45-6789"
        assert detector.has_pii(text) is True


class TestCustomPatterns:
    """Test custom PII pattern functionality"""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        return PIIDetector()

    def test_add_custom_pattern(self, detector: PIIDetector) -> None:
        """Test adding custom pattern"""
        detector.add_custom_pattern("employee_id", r"EMP\d{6}")
        result = detector.detect("My ID is EMP123456")
        assert "custom_employee_id" in result
        assert "EMP123456" in result["custom_employee_id"]

    def test_custom_pattern_empty_name(self, detector: PIIDetector) -> None:
        """Test that empty pattern name raises ValueError"""
        with pytest.raises(ValueError):
            detector.add_custom_pattern("", r"test")

    def test_custom_pattern_invalid_regex(self, detector: PIIDetector) -> None:
        """Test that invalid regex raises ValueError"""
        with pytest.raises(ValueError):
            detector.add_custom_pattern("bad_pattern", r"[invalid(")

    def test_remove_custom_pattern(self, detector: PIIDetector) -> None:
        """Test removing custom pattern"""
        detector.add_custom_pattern("test", r"TEST\d+")
        assert detector.remove_custom_pattern("test") is True
        assert detector.remove_custom_pattern("test") is False

    def test_get_pattern_types(self, detector: PIIDetector) -> None:
        """Test retrieving pattern types"""
        detector.add_custom_pattern("custom", r"test")
        types = detector.get_pattern_types()
        assert "email" in types
        assert "custom_custom" in types


class TestMaskPII:
    """Test PII masking functionality"""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        return PIIDetector()

    def test_mask_email(self, detector: PIIDetector) -> None:
        """Test masking email address"""
        masked = detector.mask_pii("john@example.com")
        assert "john@example.com" not in masked
        assert "*" in masked

    def test_mask_multiple_pii(self, detector: PIIDetector) -> None:
        """Test masking multiple PII types"""
        text = "Email: john@example.com, SSN: 123-45-6789"
        masked = detector.mask_pii(text)
        assert "john@example.com" not in masked
        assert "123-45-6789" not in masked

    def test_mask_custom_char(self, detector: PIIDetector) -> None:
        """Test masking with custom character"""
        masked = detector.mask_pii("john@example.com", mask_char="X")
        assert "X" in masked
        assert "*" not in masked

    def test_mask_preserves_structure(self, detector: PIIDetector) -> None:
        """Test that masking preserves text structure"""
        text = "Contact: john@example.com for help"
        masked = detector.mask_pii(text)
        original_parts = text.split()
        masked_parts = masked.split()
        # Same number of words
        assert len(original_parts) == len(masked_parts)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.fixture
    def detector(self) -> PIIDetector:
        return PIIDetector()

    def test_empty_string(self, detector: PIIDetector) -> None:
        """Test detection on empty string"""
        result = detector.detect("")
        assert len(result) == 0

    def test_very_long_text(self, detector: PIIDetector) -> None:
        """Test detection on very long text"""
        text = "Hello world " * 1000 + "john@example.com"
        result = detector.detect(text)
        assert "email" in result

    def test_unicode_content(self, detector: PIIDetector) -> None:
        """Test detection with unicode characters"""
        text = "你好 john@example.com 世界"
        result = detector.detect(text)
        assert "email" in result

    def test_case_insensitivity(self, detector: PIIDetector) -> None:
        """Test case-insensitive detection"""
        result1 = detector.detect("JOHN@EXAMPLE.COM")
        result2 = detector.detect("john@example.com")
        # Both should detect email
        assert "email" in result1
        assert "email" in result2

    def test_special_characters_in_text(self, detector: PIIDetector) -> None:
        """Test detection with special characters"""
        text = "Contact: john@example.com!!! [SSN: 123-45-6789]"
        result = detector.detect(text)
        assert "email" in result
        assert "ssn" in result


class TestPerformance:
    """Test performance characteristics"""

    def test_detector_initialization(self) -> None:
        """Test detector initialization is fast"""
        import time

        start = time.time()
        for _ in range(100):
            PIIDetector()
        elapsed = time.time() - start
        # Should initialize 100 detectors in less than 1 second
        assert elapsed < 1.0

    def test_detection_speed(self) -> None:
        """Test detection speed on text with PII"""
        detector = PIIDetector()
        text = "john@example.com " * 100

        import time

        start = time.time()
        for _ in range(10):
            detector.detect(text)
        elapsed = time.time() - start
        # Should complete 10 scans in less than 1 second
        assert elapsed < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
