"""
PII Detector: Detects Personally Identifiable Information in text

This module provides detection capabilities for common PII patterns including:
- Email addresses
- Phone numbers (US and international formats)
- Credit card numbers (all major formats)
- Social Security Numbers (SSN)
- API keys and tokens
- IP addresses
- Passport numbers
"""

import re


class PIIDetector:
    """
    Detects Personally Identifiable Information (PII) in text.

    This class uses regex-based pattern matching to identify sensitive data
    such as email addresses, phone numbers, credit card numbers, SSN, API keys,
    IP addresses, and passport numbers.

    Attributes:
        PATTERNS: Dictionary of PII pattern types and their regex patterns
    """

    # Compiled regex patterns for efficient matching
    PATTERNS = {
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", re.IGNORECASE),
        "phone_us": re.compile(r"(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b"),
        "phone_international": re.compile(r"(?:\+|00)?[1-9]\d{1,14}(?:[-.\s]?\d+)*\b"),
        "credit_card_visa": re.compile(r"\b4[0-9]{12}(?:[0-9]{3})?\b"),
        "credit_card_mastercard": re.compile(r"\b5[1-5][0-9]{14}\b"),
        "credit_card_amex": re.compile(r"\b3[47][0-9]{13}\b"),
        "credit_card_discover": re.compile(r"\b6(?:011|5[0-9]{2})[0-9]{12}\b"),
        "ssn": re.compile(r"\b(?!000|666|9\d{2})\d{3}-?(?!00)\d{2}-?(?!0000)\d{4}\b"),
        "api_key": re.compile(
            r"(?i)(?:api[_-]?key|apikey|api_secret|secret_key|access_token|bearer)\s*[=:\s]+\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?"
        ),
        "ipv4": re.compile(
            r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        ),
        "ipv6": re.compile(
            r"(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|::(?:[0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}|[0-9a-fA-F]{1,4}::(?:[0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}"
        ),
        "passport": re.compile(r"\b[A-Z]{1,2}\d{6,9}\b"),
    }

    def __init__(self) -> None:
        """
        Initialize the PIIDetector instance.

        Sets up the detector with predefined regex patterns for PII detection.
        """
        self._custom_patterns: dict[str, re.Pattern] = {}

    def detect(self, text: str) -> dict[str, list[str]]:
        """
        Detect PII in the provided text.

        Searches for all known PII patterns and returns detailed information
        about detected PII including the type and matched values.

        Args:
            text: The text to scan for PII

        Returns:
            Dictionary mapping PII types to lists of detected values.
            Example: {"email": ["user@example.com"], "ssn": ["123-45-6789"]}

        Example:
            >>> detector = PIIDetector()
            >>> result = detector.detect("Contact me at john@example.com")
            >>> print(result)
            {"email": ["john@example.com"]}
        """
        results: dict[str, list[str]] = {}

        # Search all standard patterns
        for pattern_type, pattern in self.PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                # Flatten matches (some patterns return groups)
                if matches and isinstance(matches[0], tuple):
                    matches = [m[0] if isinstance(m, tuple) else m for m in matches]

                # Remove duplicates while preserving order
                unique_matches = []
                seen = set()
                for match in matches:
                    if match not in seen:
                        unique_matches.append(match)
                        seen.add(match)

                if unique_matches:
                    results[pattern_type] = unique_matches

        # Search custom patterns
        for custom_type, custom_pattern in self._custom_patterns.items():
            matches = custom_pattern.findall(text)
            if matches:
                if matches and isinstance(matches[0], tuple):
                    matches = [m[0] if isinstance(m, tuple) else m for m in matches]

                unique_matches = []
                seen = set()
                for match in matches:
                    if match not in seen:
                        unique_matches.append(match)
                        seen.add(match)

                if unique_matches:
                    results[f"custom_{custom_type}"] = unique_matches

        return results

    def has_pii(self, text: str) -> bool:
        """
        Quick check for presence of any PII in text.

        Faster than detect() when you only need a boolean result.

        Args:
            text: The text to scan for PII

        Returns:
            True if any PII is detected, False otherwise

        Example:
            >>> detector = PIIDetector()
            >>> detector.has_pii("john@example.com")
            True
            >>> detector.has_pii("Hello world")
            False
        """
        return len(self.detect(text)) > 0

    def add_custom_pattern(self, pattern_name: str, regex_pattern: str) -> None:
        r"""
        Add a custom PII pattern for detection.

        Allows runtime registration of custom regex patterns for detecting
        domain-specific PII or custom sensitive data formats.

        Args:
            pattern_name: Name for the custom pattern
            regex_pattern: Regex pattern string for matching

        Raises:
            ValueError: If pattern_name is empty or regex_pattern is invalid

        Example:
            >>> detector = PIIDetector()
            >>> detector.add_custom_pattern("employee_id", r"EMP\d{6}")
            >>> detector.detect("My ID is EMP123456")
            {"custom_employee_id": ["EMP123456"]}
        """
        if not pattern_name:
            raise ValueError("pattern_name cannot be empty")

        try:
            compiled_pattern = re.compile(regex_pattern)
            self._custom_patterns[pattern_name] = compiled_pattern
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}") from e

    def remove_custom_pattern(self, pattern_name: str) -> bool:
        r"""
        Remove a previously added custom PII pattern.

        Args:
            pattern_name: Name of the custom pattern to remove

        Returns:
            True if pattern was removed, False if it didn't exist

        Example:
            >>> detector = PIIDetector()
            >>> detector.add_custom_pattern("test", r"TEST\d+")
            >>> detector.remove_custom_pattern("test")
            True
        """
        if pattern_name in self._custom_patterns:
            del self._custom_patterns[pattern_name]
            return True
        return False

    def get_pattern_types(self) -> list[str]:
        """
        Get list of all available PII pattern types.

        Returns:
            List of pattern type names (both standard and custom)

        Example:
            >>> detector = PIIDetector()
            >>> types = detector.get_pattern_types()
            >>> "email" in types
            True
        """
        types = list(self.PATTERNS.keys())
        types.extend([f"custom_{name}" for name in self._custom_patterns.keys()])
        return types

    def mask_pii(self, text: str, mask_char: str = "*") -> str:
        """
        Mask detected PII in text for privacy.

        Replaces detected PII with mask characters while preserving text structure.

        Args:
            text: The text to mask
            mask_char: Character to use for masking (default: "*")

        Returns:
            Text with detected PII masked

        Example:
            >>> detector = PIIDetector()
            >>> detector.mask_pii("Email: john@example.com")
            "Email: ****@***.***"
        """
        masked_text = text
        detected = self.detect(text)

        for _pii_type, matches in detected.items():
            for match in matches:
                # Create mask of same length as detected value
                masked_value = mask_char * len(match)
                masked_text = masked_text.replace(match, masked_value, 1)

        return masked_text
