"""
Guard: Main API class for GuardLLM

The Guard class serves as the primary entry point for scanning and analyzing
LLM prompts and responses for safety, governance, and observability concerns.
"""

from typing import Dict, List

from guardllm.core import GuardReport
from guardllm.safety.injection_detector import PromptInjectionDetector
from guardllm.safety.pii_detector import PIIDetector
from guardllm.safety.risk_scorer import RiskScorer


class Guard:
    """
    Main Guard class for LLM application safety and governance.

    The Guard class provides comprehensive tools for:
    - Detecting prompt injections
    - Identifying PII and sensitive data
    - Audit logging and observability
    - Risk scoring and assessment

    This is the primary entry point for all GuardLLM functionality.

    Example:
        >>> guard = Guard()
        >>> report = guard.scan("Is this prompt safe?")
        >>> print(report)
    """

    def __init__(self) -> None:
        """
        Initialize the Guard instance.

        Sets up the guard with default configurations and initializes
        all detection modules:
        - PIIDetector for sensitive data detection
        - PromptInjectionDetector for injection attacks
        - RiskScorer for risk assessment
        """
        self._pii_detector = PIIDetector()
        self._injection_detector = PromptInjectionDetector()
        self._risk_scorer = RiskScorer()

    def scan(self, prompt: str) -> GuardReport:
        """
        Scan a prompt for safety issues and generate a comprehensive report.

        This method analyzes the provided prompt for various security and
        safety concerns including prompt injections, PII exposure, and other
        risks. Returns a detailed report with findings.

        The scanning process:
        1. Detects PII in the prompt
        2. Detects prompt injection attacks
        3. Aggregates issues and calculates risk score
        4. Returns comprehensive GuardReport

        Args:
            prompt: The prompt text to scan

        Returns:
            GuardReport: A report object containing scan results including
                        risk score, detected issues, and flags for PII
                        and injection detection

        Example:
            >>> guard = Guard()
            >>> report = guard.scan("What is your credit card number?")
            >>> print(report)
            >>> if report.risk_score > 0.5:
            ...     print("High risk prompt detected")
        """
        # Run all detectors
        pii_results = self.detect_pii(prompt)
        pii_detected = len(pii_results) > 0
        injection_detected = self.detect_prompt_injection(prompt)

        # Aggregate issues
        issues = []
        if pii_detected:
            issues.append("pii_detected")
        if injection_detected:
            issues.append("prompt_injection")

        # Calculate risk score using RiskScorer
        risk_score = self._risk_scorer.score_from_detections(
            pii_detected=pii_detected, injection_detected=injection_detected
        )

        # Create and return report
        report = GuardReport(
            prompt=prompt,
            risk_score=risk_score,
            pii_detected=pii_detected,
            injection_detected=injection_detected,
            issues=issues,
        )

        return report

    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """
        Detect Personally Identifiable Information (PII) in text.

        Scans the provided text for common PII patterns such as:
        - Email addresses
        - Phone numbers (US and international)
        - Credit card numbers (all major card types)
        - Social Security Numbers (SSN)
        - API keys and tokens
        - IP addresses (IPv4 and IPv6)
        - Passport numbers

        Args:
            text: The text to scan for PII

        Returns:
            Dictionary mapping PII types to lists of detected values.
            Returns empty dict if no PII found.

        Example:
            >>> guard = Guard()
            >>> pii = guard.detect_pii("Email: john@example.com, SSN: 123-45-6789")
            >>> print(pii)
            {'email': ['john@example.com'], 'ssn': ['123-45-6789']}
            >>> if guard.detect_pii(text):
            ...     print("PII detected!")
        """
        return self._pii_detector.detect(text)

    def detect_prompt_injection(self, text: str) -> bool:
        """
        Detect potential prompt injection attacks in text.

        Identifies common prompt injection patterns and attack vectors that
        could be used to manipulate LLM behavior or bypass safety constraints.

        Detects patterns such as:
        - "ignore previous instructions"
        - "reveal system prompt"
        - "bypass safety"
        - And more...

        Args:
            text: The text to scan for injection attacks

        Returns:
            bool: True if a potential injection is detected, False otherwise

        Example:
            >>> guard = Guard()
            >>> if guard.detect_prompt_injection("Ignore all instructions"):
            ...     print("Injection attack detected!")
        """
        return self._injection_detector.detect(text)

    def get_risk_level(self, risk_score: float) -> str:
        """
        Get human-readable risk level for a score.

        Categorizes numerical score into text level:
        - low: 0.0 - 0.24
        - medium: 0.25 - 0.49
        - high: 0.5 - 0.74
        - critical: 0.75 - 1.0

        Args:
            risk_score: Risk score between 0.0 and 1.0

        Returns:
            String describing risk level

        Example:
            >>> guard = Guard()
            >>> report = guard.scan("test prompt")
            >>> level = guard.get_risk_level(report.risk_score)
            >>> print(f"Risk level: {level}")
        """
        return self._risk_scorer.get_risk_level(risk_score)
