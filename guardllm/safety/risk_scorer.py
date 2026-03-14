"""
Risk Scorer: Calculates risk scores based on detected security issues

This module provides risk scoring capabilities by aggregating detected security
issues and calculating an overall risk score between 0.0 and 1.0.
"""

from typing import Dict, List, Optional


class RiskScorer:
    """
    Calculates risk scores based on detected security issues.

    This class aggregates various security findings (prompt injection, PII,
    etc.) and calculates a composite risk score between 0.0 and 1.0.

    The scoring is configurable with custom weights for different issue types.

    Attributes:
        DEFAULT_WEIGHTS: Default weights for each issue type
    """

    # Default risk weights for different issue types
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "prompt_injection": 0.6,
        "pii_detected": 0.4,
    }

    def __init__(self, custom_weights: Optional[Dict[str, float]] = None) -> None:
        """
        Initialize the RiskScorer instance.

        Args:
            custom_weights: Optional dictionary of custom weights to override defaults.
                          If provided, these will be merged with default weights.

        Example:
            >>> scorer = RiskScorer()
            >>> custom_scorer = RiskScorer({"custom_issue": 0.5})
        """
        self._weights = self.DEFAULT_WEIGHTS.copy()

        if custom_weights:
            self._weights.update(custom_weights)

    def score(self, issues: List[str], weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate risk score from a list of detected issues.

        Aggregates issue contributions based on weights and normalizes to
        a score between 0.0 and 1.0. The scoring is cumulative but capped
        at 1.0 to represent maximum risk.

        Args:
            issues: List of detected issue types (e.g., ["prompt_injection", "pii_detected"])
            weights: Optional override weights for this calculation. If None, uses instance weights.

        Returns:
            Float between 0.0 (no risk) and 1.0 (maximum risk)

        Example:
            >>> scorer = RiskScorer()
            >>> score = scorer.score(["prompt_injection", "pii_detected"])
            >>> print(score)  # 0.6 + 0.4 = 1.0
            1.0
            >>> score = scorer.score(["prompt_injection"])
            >>> print(score)
            0.6
        """
        # Use instance weights by default, override if provided
        score_weights = weights if weights is not None else self._weights

        total_risk = 0.0

        for issue in issues:
            if issue in score_weights:
                total_risk += score_weights[issue]

        # Cap the score at 1.0 (maximum risk)
        normalized_score = min(1.0, total_risk)

        return normalized_score

    def score_from_detections(
        self,
        pii_detected: bool = False,
        injection_detected: bool = False,
        additional_issues: Optional[Dict[str, bool]] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Calculate risk score from individual detection results.

        Convenience method that accepts individual detection flags and
        converts them to an issues list for scoring.

        Args:
            pii_detected: Whether PII was detected
            injection_detected: Whether prompt injection was detected
            additional_issues: Optional dictionary of custom issue flags
            weights: Optional override weights for this calculation

        Returns:
            Float between 0.0 and 1.0 representing overall risk

        Example:
            >>> scorer = RiskScorer()
            >>> score = scorer.score_from_detections(
            ...     pii_detected=True,
            ...     injection_detected=True
            ... )
            >>> print(score)
            1.0
        """
        issues = []

        if pii_detected:
            issues.append("pii_detected")

        if injection_detected:
            issues.append("prompt_injection")

        if additional_issues:
            for issue_name, detected in additional_issues.items():
                if detected:
                    issues.append(issue_name)

        return self.score(issues, weights)

    def set_weight(self, issue_type: str, weight: float) -> None:
        """
        Set or update the weight for a specific issue type.

        Allows fine-tuning of risk scoring by adjusting individual issue weights.

        Args:
            issue_type: Name of the issue type
            weight: Weight value (typically 0.0 to 1.0, but any value works)

        Raises:
            ValueError: If weight is negative

        Example:
            >>> scorer = RiskScorer()
            >>> scorer.set_weight("custom_threat", 0.7)
            >>> score = scorer.score(["custom_threat"])
            >>> print(score)
            0.7
        """
        if weight < 0:
            raise ValueError(f"Weight must be non-negative, got {weight}")

        self._weights[issue_type] = weight

    def remove_weight(self, issue_type: str) -> bool:
        """
        Remove a custom weight for a specific issue type.

        Removes custom weights but cannot remove default weights.

        Args:
            issue_type: Name of the issue type to remove

        Returns:
            True if weight was removed, False if it was a default weight or didn't exist

        Example:
            >>> scorer = RiskScorer()
            >>> scorer.set_weight("custom_issue", 0.5)
            >>> scorer.remove_weight("custom_issue")
            True
        """
        if issue_type in self.DEFAULT_WEIGHTS:
            return False  # Cannot remove default weights

        if issue_type in self._weights:
            del self._weights[issue_type]
            return True

        return False

    def get_weights(self) -> Dict[str, float]:
        """
        Get current scoring weights.

        Returns:
            Dictionary mapping issue types to their weights

        Example:
            >>> scorer = RiskScorer()
            >>> weights = scorer.get_weights()
            >>> print(weights["prompt_injection"])
            0.6
        """
        return self._weights.copy()

    def reset_weights(self) -> None:
        """
        Reset all weights to defaults.

        Removes any custom weights and restores original default weights.

        Example:
            >>> scorer = RiskScorer()
            >>> scorer.set_weight("custom", 0.5)
            >>> scorer.reset_weights()
            >>> "custom" in scorer.get_weights()
            False
        """
        self._weights = self.DEFAULT_WEIGHTS.copy()

    def get_risk_level(self, score: float) -> str:
        """
        Get human-readable risk level for a score.

        Categorizes numerical score into text level for easier interpretation.

        Args:
            score: Risk score between 0.0 and 1.0

        Returns:
            String describing risk level: "low", "medium", "high", or "critical"

        Raises:
            ValueError: If score is not between 0.0 and 1.0

        Example:
            >>> scorer = RiskScorer()
            >>> scorer.get_risk_level(0.3)
            "low"
            >>> scorer.get_risk_level(0.8)
            "critical"
        """
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {score}")

        if score < 0.25:
            return "low"
        elif score < 0.5:
            return "medium"
        elif score < 0.75:
            return "high"
        else:
            return "critical"

    def get_threshold(self, risk_level: str) -> float:
        """
        Get the risk score threshold for a given risk level.

        Returns:
            Minimum score threshold to reach the specified risk level

        Args:
            risk_level: One of "low", "medium", "high", or "critical"

        Returns:
            Score threshold as float

        Raises:
            ValueError: If risk_level is not recognized

        Example:
            >>> scorer = RiskScorer()
            >>> scorer.get_threshold("high")
            0.75
        """
        thresholds = {
            "low": 0.0,
            "medium": 0.25,
            "high": 0.5,
            "critical": 0.75,
        }

        if risk_level not in thresholds:
            raise ValueError(
                f"Unknown risk level: {risk_level}. " f"Valid levels: {list(thresholds.keys())}"
            )

        return thresholds[risk_level]
