"""
GuardLLM: A Responsible AI Toolkit for LLM Applications

This package provides safety, governance, and observability features for LLM applications.

Modules:
    core: Core data structures (GuardReport)
    safety: Safety detection and risk assessment
    governance: Policy enforcement and compliance controls
    observability: Logging, monitoring, and audit trails
    utils: Utility functions and helpers

Main Classes:
    Guard: Main entry point for scanning prompts
    GuardReport: Results of safety scans
    GuardConfig: Configuration for Guard behavior
    AuditLogger: Structured audit logging

Custom Exceptions:
    GuardLLMException: Base exception
    ConfigurationError: Configuration issues
    DetectionError: Detection process errors
    LoggingError: Logging failures
    ScanError: Scan operation errors

Example:
    >>> from guardllm import Guard, GuardReport
    >>> guard = Guard()
    >>> report = guard.scan("Your prompt here")
    >>> print(report)
"""

from guardllm.config import GuardConfig, GuardConfigBuilder
from guardllm.core import GuardReport
from guardllm.exceptions import (
    ConfigurationError,
    DetectionError,
    GuardLLMException,
    LoggingError,
    PatternError,
    ScanError,
    ValidationError,
)
from guardllm.guard import Guard
from guardllm.observability import AuditLogger

__all__ = [
    "Guard",
    "GuardReport",
    "GuardConfig",
    "GuardConfigBuilder",
    "AuditLogger",
    "GuardLLMException",
    "ConfigurationError",
    "DetectionError",
    "LoggingError",
    "ScanError",
    "PatternError",
    "ValidationError",
]

__version__ = "0.1.0"
__author__ = "GuardLLM Contributors"
__license__ = "MIT"
