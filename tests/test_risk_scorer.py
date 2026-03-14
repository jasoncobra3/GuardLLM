"""
Test suite for RiskScorer

Tests risk scoring functionality including calculation, weight management,
and risk level categorization.
"""

import pytest
from guardllm.safety.risk_scorer import RiskScorer


class TestRiskScorerBasic:
    """Test basic risk scoring functionality"""

    @pytest.fixture
    def scorer(self) -> RiskScorer:
        """Create a fresh RiskScorer instance for each test"""
        return RiskScorer()

    def test_score_no_issues(self, scorer: RiskScorer) -> None:
        """Test scoring with no issues"""
        score = scorer.score([])
        assert score == 0.0

    def test_score_single_injection(self, scorer: RiskScorer) -> None:
        """Test scoring with prompt injection only"""
        score = scorer.score(["prompt_injection"])
        assert score == 0.6

    def test_score_single_pii(self, scorer: RiskScorer) -> None:
        """Test scoring with PII only"""
        score = scorer.score(["pii_detected"])
        assert score == 0.4

    def test_score_both_issues(self, scorer: RiskScorer) -> None:
        """Test scoring with both injection and PII"""
        score = scorer.score(["prompt_injection", "pii_detected"])
        assert score == 1.0  # 0.6 + 0.4 = 1.0

    def test_score_capped_at_one(self, scorer: RiskScorer) -> None:
        """Test that score is capped at 1.0"""
        # Even with multiple heavy issues, should not exceed 1.0
        scorer.set_weight("issue1", 0.8)
        scorer.set_weight("issue2", 0.7)
        score = scorer.score(["issue1", "issue2"])
        assert score == 1.0
        assert score <= 1.0

    def test_score_with_unknown_issue(self, scorer: RiskScorer) -> None:
        """Test scoring ignores unknown issue types"""
        score = scorer.score(["unknown_issue"])
        assert score == 0.0

    def test_score_with_mixed_known_unknown(self, scorer: RiskScorer) -> None:
        """Test scoring with mix of known and unknown issues"""
        score = scorer.score(["prompt_injection", "unknown_issue"])
        assert score == 0.6  # Only known issue counts


class TestScoreFromDetections:
    """Test score_from_detections convenience method"""

    @pytest.fixture
    def scorer(self) -> RiskScorer:
        return RiskScorer()

    def test_from_detections_no_issues(self, scorer: RiskScorer) -> None:
        """Test from_detections with no issues detected"""
        score = scorer.score_from_detections()
        assert score == 0.0

    def test_from_detections_pii_only(self, scorer: RiskScorer) -> None:
        """Test from_detections with PII only"""
        score = scorer.score_from_detections(pii_detected=True)
        assert score == 0.4

    def test_from_detections_injection_only(self, scorer: RiskScorer) -> None:
        """Test from_detections with injection only"""
        score = scorer.score_from_detections(injection_detected=True)
        assert score == 0.6

    def test_from_detections_both(self, scorer: RiskScorer) -> None:
        """Test from_detections with both types"""
        score = scorer.score_from_detections(pii_detected=True, injection_detected=True)
        assert score == 1.0

    def test_from_detections_additional_issues(self, scorer: RiskScorer) -> None:
        """Test from_detections with additional custom issues"""
        scorer.set_weight("custom_issue", 0.3)
        score = scorer.score_from_detections(
            injection_detected=True, additional_issues={"custom_issue": True}
        )
        assert score == pytest.approx(0.9)  # 0.6 + 0.3


class TestWeightManagement:
    """Test weight management functionality"""

    @pytest.fixture
    def scorer(self) -> RiskScorer:
        return RiskScorer()

    def test_default_weights(self, scorer: RiskScorer) -> None:
        """Test default weights are loaded"""
        weights = scorer.get_weights()
        assert weights["prompt_injection"] == 0.6
        assert weights["pii_detected"] == 0.4

    def test_set_weight(self, scorer: RiskScorer) -> None:
        """Test setting a weight"""
        scorer.set_weight("new_issue", 0.5)
        weights = scorer.get_weights()
        assert weights["new_issue"] == 0.5

    def test_set_weight_negative(self, scorer: RiskScorer) -> None:
        """Test that negative weights are rejected"""
        with pytest.raises(ValueError):
            scorer.set_weight("issue", -0.5)

    def test_set_weight_zero(self, scorer: RiskScorer) -> None:
        """Test that zero weight is allowed"""
        scorer.set_weight("issue", 0.0)
        score = scorer.score(["issue"])
        assert score == 0.0

    def test_override_default_weight(self, scorer: RiskScorer) -> None:
        """Test overriding default weight"""
        scorer.set_weight("prompt_injection", 0.8)
        score = scorer.score(["prompt_injection"])
        assert score == 0.8

    def test_remove_custom_weight(self, scorer: RiskScorer) -> None:
        """Test removing custom weight"""
        scorer.set_weight("custom", 0.5)
        assert scorer.remove_weight("custom") is True
        assert scorer.remove_weight("custom") is False

    def test_cannot_remove_default_weight(self, scorer: RiskScorer) -> None:
        """Test that default weights cannot be removed"""
        assert scorer.remove_weight("prompt_injection") is False
        weights = scorer.get_weights()
        assert "prompt_injection" in weights

    def test_reset_weights(self, scorer: RiskScorer) -> None:
        """Test resetting weights to defaults"""
        scorer.set_weight("prompt_injection", 0.9)
        scorer.set_weight("custom", 0.5)
        scorer.reset_weights()

        weights = scorer.get_weights()
        assert weights["prompt_injection"] == 0.6  # Back to default
        assert "custom" not in weights  # Custom removed

    def test_custom_weights_on_init(self) -> None:
        """Test initializing with custom weights"""
        custom = {"custom_issue": 0.7}
        scorer = RiskScorer(custom_weights=custom)
        weights = scorer.get_weights()
        assert weights["custom_issue"] == 0.7
        assert weights["prompt_injection"] == 0.6  # Defaults still present


class TestRiskLevels:
    """Test risk level categorization"""

    @pytest.fixture
    def scorer(self) -> RiskScorer:
        return RiskScorer()

    def test_risk_level_low(self, scorer: RiskScorer) -> None:
        """Test low risk categorization"""
        assert scorer.get_risk_level(0.0) == "low"
        assert scorer.get_risk_level(0.15) == "low"
        assert scorer.get_risk_level(0.24) == "low"

    def test_risk_level_medium(self, scorer: RiskScorer) -> None:
        """Test medium risk categorization"""
        assert scorer.get_risk_level(0.25) == "medium"
        assert scorer.get_risk_level(0.4) == "medium"
        assert scorer.get_risk_level(0.49) == "medium"

    def test_risk_level_high(self, scorer: RiskScorer) -> None:
        """Test high risk categorization"""
        assert scorer.get_risk_level(0.5) == "high"
        assert scorer.get_risk_level(0.65) == "high"
        assert scorer.get_risk_level(0.74) == "high"

    def test_risk_level_critical(self, scorer: RiskScorer) -> None:
        """Test critical risk categorization"""
        assert scorer.get_risk_level(0.75) == "critical"
        assert scorer.get_risk_level(0.9) == "critical"
        assert scorer.get_risk_level(1.0) == "critical"

    def test_risk_level_invalid_score(self, scorer: RiskScorer) -> None:
        """Test invalid score raises error"""
        with pytest.raises(ValueError):
            scorer.get_risk_level(-0.1)
        with pytest.raises(ValueError):
            scorer.get_risk_level(1.1)

    def test_get_threshold(self, scorer: RiskScorer) -> None:
        """Test getting threshold for risk level"""
        assert scorer.get_threshold("low") == 0.0
        assert scorer.get_threshold("medium") == 0.25
        assert scorer.get_threshold("high") == 0.5
        assert scorer.get_threshold("critical") == 0.75

    def test_get_threshold_invalid(self, scorer: RiskScorer) -> None:
        """Test invalid risk level raises error"""
        with pytest.raises(ValueError):
            scorer.get_threshold("extreme")


class TestScoringScenarios:
    """Test realistic scoring scenarios"""

    @pytest.fixture
    def scorer(self) -> RiskScorer:
        return RiskScorer()

    def test_phishing_attempt(self, scorer: RiskScorer) -> None:
        """Test scoring a phishing attempt"""
        # Phishing: request for PII + injection attempt
        score = scorer.score(["pii_detected", "prompt_injection"])
        assert score == 1.0
        assert scorer.get_risk_level(score) == "critical"

    def test_information_request(self, scorer: RiskScorer) -> None:
        """Test scoring a benign information request"""
        score = scorer.score([])
        assert score == 0.0
        assert scorer.get_risk_level(score) == "low"

    def test_injection_only_attempt(self, scorer: RiskScorer) -> None:
        """Test scoring injection-only attack"""
        score = scorer.score(["prompt_injection"])
        assert 0.5 < score < 1.0
        assert scorer.get_risk_level(score) == "high"

    def test_accidental_pii_exposure(self, scorer: RiskScorer) -> None:
        """Test scoring accidental PII mention"""
        score = scorer.score(["pii_detected"])
        assert 0.2 < score < 0.5
        assert scorer.get_risk_level(score) in ["medium", "high"]


class TestOverrideWeights:
    """Test weight overrides in score method"""

    @pytest.fixture
    def scorer(self) -> RiskScorer:
        return RiskScorer()

    def test_score_with_override_weights(self, scorer: RiskScorer) -> None:
        """Test passing override weights to score method"""
        override_weights = {"prompt_injection": 0.9}
        score = scorer.score(["prompt_injection"], weights=override_weights)
        assert score == 0.9

    def test_override_does_not_modify_instance(self, scorer: RiskScorer) -> None:
        """Test that override weights don't modify instance"""
        original_weight = scorer.get_weights()["prompt_injection"]
        scorer.score(["prompt_injection"], weights={"prompt_injection": 0.9})
        assert scorer.get_weights()["prompt_injection"] == original_weight

    def test_override_in_from_detections(self, scorer: RiskScorer) -> None:
        """Test weight override in score_from_detections"""
        override_weights = {"pii_detected": 0.8}
        score = scorer.score_from_detections(pii_detected=True, weights=override_weights)
        assert score == 0.8


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.fixture
    def scorer(self) -> RiskScorer:
        return RiskScorer()

    def test_empty_issue_list(self, scorer: RiskScorer) -> None:
        """Test scoring empty list"""
        score = scorer.score([])
        assert score == 0.0

    def test_duplicate_issues(self, scorer: RiskScorer) -> None:
        """Test scoring with duplicate issues"""
        # Duplicates are counted separately and accumulate
        score = scorer.score(["prompt_injection", "prompt_injection"])
        assert score == 1.0  # 0.6 + 0.6 = 1.2, capped at 1.0

    def test_very_high_weight(self, scorer: RiskScorer) -> None:
        """Test with very high custom weight"""
        scorer.set_weight("critical_issue", 10.0)
        score = scorer.score(["critical_issue"])
        assert score == 1.0  # Capped at 1.0

    def test_very_low_weight(self, scorer: RiskScorer) -> None:
        """Test with very low weight"""
        scorer.set_weight("minor_issue", 0.001)
        score = scorer.score(["minor_issue"])
        assert 0.0 < score < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
