"""
Observability module for GuardLLM.

Provides logging, monitoring, and audit trail features:
- Audit logging
- Metrics collection
- Event tracking
- Integration with monitoring systems

Exports:
    AuditLogger: Structured logging for GuardLLM scans and detections
"""

from guardllm.observability.audit_logger import AuditLogger

__all__ = ["AuditLogger"]
