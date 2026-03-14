"""
Prompt Injection Detector

This module provides detection capabilities for common prompt injection attacks.
It identifies patterns and phrases commonly used in prompt injection attempts.
"""


class PromptInjectionDetector:
    """
    Detects prompt injection attacks in text.

    This class identifies common prompt injection patterns and phrases that
    could be used to manipulate LLM behavior or bypass safety constraints.

    Supports detection of:
    - Direct instruction overrides
    - System prompt revelation attempts
    - Role-playing/jailbreak attempts
    - Safety bypass attempts
    - And more...

    Attributes:
        INJECTION_PHRASES: List of known prompt injection phrases to detect
    """

    # Known prompt injection phrases and patterns
    INJECTION_PHRASES = [
        # Direct instruction overrides
        "ignore previous instructions",
        "ignore all previous instructions",
        "disregard all previous instructions",
        "forget all previous instructions",
        "erase all previous instructions",
        # System prompt revelation
        "reveal system prompt",
        "show system prompt",
        "what is your system prompt",
        "what is the system prompt",
        "print system prompt",
        "display system prompt",
        # Safety bypasses
        "bypass safety",
        "bypass all safety",
        "override safety",
        "disable safety",
        "circumvent safety",
        "break safety rules",
        # Role-playing and jailbreak attempts
        "enter developer mode",
        "enable developer mode",
        "activate developer mode",
        "pretend you are",
        "act as if you are",
        "act as",
        "roleplay as",
        "role-play as",
        "emulate",
        "simulate being",
        "jailbreak",
        # Step-by-step attempts
        "step by step",
        "step-by-step",
        # Instruction following
        "follow my instructions",
        "follow these instructions",
        "follow the instructions",
        "respond to the instructions",
        # Mode switching
        "switch to",
        "switch mode",
        "change mode",
        "change your mode",
        # Reality/context distortion
        "pretend this is",
        "assume this is",
        "imagine that",
        "hypothetically",
        "what if",
        "in a fictional scenario",
        # Direct prompt access
        "what was your prompt",
        "what was my prompt",
        "what is the initial prompt",
        "show me the prompt",
        "reveal the prompt",
        # Token/context manipulation
        "new conversation",
        "reset conversation",
        "clear history",
        "start fresh",
        # Authority bypasses
        "i am an admin",
        "i am your creator",
        "i am your developer",
        "administrator override",
        "admin mode",
        # Code execution attempts
        "execute code",
        "run code",
        "eval",
        "exec",
        "execute shell command",
        # Alternative framing
        "test mode",
        "debug mode",
        "training mode",
        "sandbox mode",
    ]

    def __init__(self) -> None:
        """
        Initialize the PromptInjectionDetector instance.

        Sets up the detector with all injection phrases.
        """
        self._custom_phrases = []

    def detect(self, text: str) -> bool:
        """
        Detect prompt injection attacks in the provided text.

        Searches for known prompt injection patterns in the text by converting
        it to lowercase and checking if any of the known injection phrases
        appear in it.

        Args:
            text: The text to scan for prompt injection attacks

        Returns:
            bool: True if a prompt injection pattern is detected, False otherwise

        Example:
            >>> detector = PromptInjectionDetector()
            >>> detector.detect("Please ignore previous instructions")
            True
            >>> detector.detect("Hello, how are you?")
            False
        """
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()

        # Check if any injection phrase exists in the text
        for phrase in self.INJECTION_PHRASES:
            if phrase in text_lower:
                return True

        # Check custom phrases
        for phrase in self._custom_phrases:
            if phrase in text_lower:
                return True

        return False

    def detect_with_details(self, text: str) -> dict:
        """
        Detect prompt injection attacks and return matching patterns.

        Searches for all matching injection patterns and returns detailed
        information about which patterns were detected.

        Args:
            text: The text to scan for prompt injection attacks

        Returns:
            Dictionary containing:
                - detected: Boolean indicating if injection was detected
                - matches: List of matched injection phrases
                - count: Number of unique patterns matched
                - risk_level: Estimated risk level (low, medium, high, critical)

        Example:
            >>> detector = PromptInjectionDetector()
            >>> result = detector.detect_with_details("ignore previous instructions")
            >>> print(result)
            {'detected': True, 'matches': ['ignore previous instructions'], 'count': 1, 'risk_level': 'high'}
        """
        text_lower = text.lower()
        matched_phrases = []

        # Check standard phrases
        for phrase in self.INJECTION_PHRASES:
            if phrase in text_lower:
                matched_phrases.append(phrase)

        # Check custom phrases
        for phrase in self._custom_phrases:
            if phrase in text_lower:
                matched_phrases.append(f"custom: {phrase}")

        detected = len(matched_phrases) > 0
        count = len(set(matched_phrases))

        # Determine risk level based on match count and severity
        if not detected:
            risk_level = "low"
        elif count <= 1:
            risk_level = "medium"
        elif count <= 2:
            risk_level = "high"
        else:
            risk_level = "critical"

        # Check for multiple different categories
        categories = self._categorize_matches(matched_phrases)
        if len(categories) > 1:
            risk_level = "critical"

        return {
            "detected": detected,
            "matches": list(set(matched_phrases)),
            "count": count,
            "risk_level": risk_level,
        }

    def add_custom_phrase(self, phrase: str) -> None:
        """
        Add a custom injection phrase for detection.

        Allows runtime registration of custom phrases for domain-specific or
        organization-specific injection patterns.

        Args:
            phrase: Phrase string to detect (case-insensitive)

        Raises:
            ValueError: If phrase is empty

        Example:
            >>> detector = PromptInjectionDetector()
            >>> detector.add_custom_phrase("company confidential mode")
            >>> detector.detect("Enter company confidential mode")
            True
        """
        if not phrase or not phrase.strip():
            raise ValueError("Phrase cannot be empty")

        normalized_phrase = phrase.lower().strip()
        if normalized_phrase not in self._custom_phrases:
            self._custom_phrases.append(normalized_phrase)

    def remove_custom_phrase(self, phrase: str) -> bool:
        """
        Remove a previously added custom injection phrase.

        Args:
            phrase: Phrase to remove

        Returns:
            True if phrase was removed, False if it didn't exist

        Example:
            >>> detector = PromptInjectionDetector()
            >>> detector.add_custom_phrase("test")
            >>> detector.remove_custom_phrase("test")
            True
        """
        normalized_phrase = phrase.lower().strip()
        if normalized_phrase in self._custom_phrases:
            self._custom_phrases.remove(normalized_phrase)
            return True
        return False

    def get_all_phrases(self) -> dict:
        """
        Get all detection phrases organized by category.

        Returns:
            Dictionary mapping categories to phrase lists

        Example:
            >>> detector = PromptInjectionDetector()
            >>> phrases = detector.get_all_phrases()
            >>> print(len(phrases['direct_overrides']))
        """
        return {
            "direct_overrides": [
                p
                for p in self.INJECTION_PHRASES
                if "ignore" in p or "disregard" in p or "forget" in p or "erase" in p
            ],
            "system_prompt_revelation": [
                p for p in self.INJECTION_PHRASES if "system prompt" in p or "initial prompt" in p
            ],
            "safety_bypass": [
                p
                for p in self.INJECTION_PHRASES
                if "bypass" in p or "override" in p or "disable" in p or "circumvent" in p
            ],
            "role_play_jailbreak": [
                p
                for p in self.INJECTION_PHRASES
                if "act as" in p
                or "pretend" in p
                or "roleplay" in p
                or "jailbreak" in p
                or "emulate" in p
            ],
            "mode_switching": [
                p for p in self.INJECTION_PHRASES if "mode" in p or "switch" in p or "change" in p
            ],
            "custom": self._custom_phrases,
        }

    def _categorize_matches(self, matches: list) -> list:
        """
        Categorize matched phrases by type.

        Args:
            matches: List of matched phrases

        Returns:
            List of category names

        Example:
            >>> detector = PromptInjectionDetector()
            >>> categories = detector._categorize_matches(['ignore previous instructions'])
            >>> print(categories)
            ['direct_overrides']
        """
        categories = set()
        all_phrases = self.get_all_phrases()

        for match in matches:
            # Remove "custom: " prefix if present
            phrase = match.replace("custom: ", "")

            for category, phrases in all_phrases.items():
                if phrase in phrases:
                    categories.add(category)
                    break

        return list(categories)
