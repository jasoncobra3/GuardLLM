"""
Audit Logger: Structured logging for observability

Provides audit logging capabilities for tracking security scan results,
detection events, and generating audit trails for compliance and debugging.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from guardllm.core import GuardReport


class AuditLogger:
    """
    Structured audit logger for GuardLLM scanning and detection events.

    Provides logging capabilities for:
    - Scan results with timestamps
    - Individual detection events
    - Audit trail exports
    - Both console and file logging

    Can output logs in structured JSON format or plain text.

    Attributes:
        DEFAULT_LOG_FORMAT: Default format string for log messages
    """

    DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def __init__(
        self,
        log_file_path: Optional[str] = None,
        log_to_console: bool = True,
        log_to_file: bool = True,
        redact_sensitive_data: bool = True,
    ) -> None:
        """
        Initialize the AuditLogger instance.

        Args:
            log_file_path: Path to log file. If None, logs won't be written to file
            log_to_console: Whether to log to console output
            log_to_file: Whether to log to file
            redact_sensitive_data: Whether to mask PII in logs

        Example:
            >>> logger = AuditLogger(
            ...     log_file_path="audit.log",
            ...     log_to_console=True
            ... )
        """
        self._log_file_path = log_file_path
        self._log_to_console = log_to_console
        self._log_to_file = log_to_file
        self._redact_sensitive_data = redact_sensitive_data

        # Initialize logging
        self._logger = logging.getLogger("guardllm.audit")
        self._logger.setLevel(logging.INFO)

        # Clear existing handlers
        self._logger.handlers.clear()

        # Add console handler
        if self._log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(self.DEFAULT_LOG_FORMAT)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

        # Add file handler
        if self._log_to_file and log_file_path:
            try:
                file_handler = logging.FileHandler(log_file_path, mode="a")
                file_handler.setLevel(logging.INFO)
                formatter = logging.Formatter(self.DEFAULT_LOG_FORMAT)
                file_handler.setFormatter(formatter)
                self._logger.addHandler(file_handler)
            except IOError as e:
                self._logger.warning(f"Failed to open log file {log_file_path}: {e}")

        # In-memory log storage for exports
        self._log_entries: List[Dict[str, Any]] = []

    def log_scan(
        self,
        report: GuardReport,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a complete scan with results.

        Records a full GuardReport with all findings, timestamp, and optional
        metadata for observability and audit trail purposes.

        Args:
            report: GuardReport object with scan results
            metadata: Optional metadata dictionary with additional context

        Example:
            >>> logger = AuditLogger()
            >>> guard = Guard()
            >>> report = guard.scan("test prompt")
            >>> logger.log_scan(report, metadata={"user_id": "123"})
        """
        timestamp = datetime.utcnow().isoformat()

        # Build log entry
        entry = {
            "timestamp": timestamp,
            "event_type": "scan",
            "risk_score": report.risk_score,
            "pii_detected": report.pii_detected,
            "injection_detected": report.injection_detected,
            "issues": report.issues,
            "metadata": metadata or {},
        }

        # Add prompt to log (optionally redacted)
        if self._redact_sensitive_data:
            from guardllm.safety.pii_detector import PIIDetector
            pii_detector = PIIDetector()
            prompt_text = pii_detector.mask_pii(report.prompt)
        else:
            prompt_text = report.prompt

        entry["prompt"] = prompt_text

        # Store in memory
        self._log_entries.append(entry)

        # Log to system logger
        log_message = (
            f"Scan completed: risk_score={report.risk_score}, "
            f"pii_detected={report.pii_detected}, "
            f"injection_detected={report.injection_detected}, "
            f"issues={len(report.issues)}"
        )
        self._logger.info(log_message)

    def log_detection(
        self,
        detection_type: str,
        result: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log individual detection event.

        Records when a specific detector runs and its result, useful for
        granular monitoring and debugging.

        Args:
            detection_type: Type of detection (e.g., "pii", "injection")
            result: Boolean result of detection
            details: Optional details about the detection

        Example:
            >>> logger = AuditLogger()
            >>> logger.log_detection("pii", True, {"pii_type": "email"})
            >>> logger.log_detection("injection", False)
        """
        timestamp = datetime.utcnow().isoformat()

        entry = {
            "timestamp": timestamp,
            "event_type": "detection",
            "detection_type": detection_type,
            "result": result,
            "details": details or {},
        }

        # Store in memory
        self._log_entries.append(entry)

        # Log to system logger
        log_message = (
            f"Detection[{detection_type}]: {result}"
        )
        if details:
            log_message += f" - {details}"
        
        self._logger.info(log_message)

    def export_logs(self, format: str = "json") -> str:
        """
        Export audit logs in specified format.

        Returns all logged events in JSON or text format for external analysis
        or archival purposes.

        Args:
            format: Output format - "json" or "text"

        Returns:
            Formatted string containing all log entries

        Raises:
            ValueError: If format is not recognized

        Example:
            >>> logger = AuditLogger()
            >>> json_logs = logger.export_logs(format="json")
            >>> print(json_logs)
        """
        if format == "json":
            return json.dumps(self._log_entries, indent=2, default=str)
        elif format == "text":
            lines = []
            for entry in self._log_entries:
                timestamp = entry.get("timestamp", "unknown")
                event_type = entry.get("event_type", "unknown")
                line = f"[{timestamp}] {event_type}: {entry}"
                lines.append(line)
            return "\n".join(lines)
        else:
            raise ValueError(f"Unknown format: {format}. Use 'json' or 'text'")

    def get_log_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about logged events.

        Returns:
            Dictionary with event counts and statistics

        Example:
            >>> logger = AuditLogger()
            >>> stats = logger.get_log_statistics()
            >>> print(f"Total scans: {stats['total_scans']}")
        """
        stats = {
            "total_events": len(self._log_entries),
            "total_scans": 0,
            "total_detections": 0,
            "high_risk_scans": 0,
            "pii_detections": 0,
            "injection_detections": 0,
        }

        for entry in self._log_entries:
            if entry["event_type"] == "scan":
                stats["total_scans"] += 1
                if entry["risk_score"] > 0.7:
                    stats["high_risk_scans"] += 1
                if entry["pii_detected"]:
                    stats["pii_detections"] += 1
                if entry["injection_detected"]:
                    stats["injection_detections"] += 1
            elif entry["event_type"] == "detection":
                stats["total_detections"] += 1

        return stats

    def clear_logs(self) -> None:
        """
        Clear all stored logs.

        Clears only the in-memory logs. Logs already written to files
        are not affected.

        Example:
            >>> logger = AuditLogger()
            >>> logger.clear_logs()
        """
        self._log_entries.clear()

    def get_recent_scans(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent scan logs.

        Args:
            limit: Maximum number of scans to return

        Returns:
            List of recent scan entries

        Example:
            >>> logger = AuditLogger()
            >>> recent = logger.get_recent_scans(limit=5)
        """
        scans = [
            entry for entry in self._log_entries
            if entry["event_type"] == "scan"
        ]
        return scans[-limit:]

    def get_detection_timeline(
        self,
        detection_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get detection events with optional filtering.

        Args:
            detection_type: Optional filter by detection type

        Returns:
            List of detection events

        Example:
            >>> logger = AuditLogger()
            >>> pii_detections = logger.get_detection_timeline("pii")
        """
        detections = [
            entry for entry in self._log_entries
            if entry["event_type"] == "detection"
        ]

        if detection_type:
            detections = [
                d for d in detections
                if d["detection_type"] == detection_type
            ]

        return detections

    def write_logs_to_file(self, file_path: str, format: str = "json") -> None:
        """
        Write logs to a specific file.

        Exports current logs to a file in specified format.

        Args:
            file_path: Path to write logs to
            format: Output format - "json" or "text"

        Raises:
            IOError: If file cannot be written

        Example:
            >>> logger = AuditLogger()
            >>> logger.write_logs_to_file("audit_export.json", format="json")
        """
        try:
            content = self.export_logs(format=format)
            with open(file_path, "w") as f:
                f.write(content)
        except IOError as e:
            raise IOError(f"Failed to write logs to {file_path}: {e}")

    def get_high_risk_events(self, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Get all high-risk scan events above threshold.

        Args:
            threshold: Risk score threshold (0.0 to 1.0)

        Returns:
            List of high-risk scan entries

        Example:
            >>> logger = AuditLogger()
            >>> high_risk = logger.get_high_risk_events(threshold=0.8)
        """
        return [
            entry for entry in self._log_entries
            if entry["event_type"] == "scan"
            and entry["risk_score"] > threshold
        ]
