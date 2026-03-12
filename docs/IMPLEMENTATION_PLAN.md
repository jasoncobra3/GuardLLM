# GuardLLM Implementation Plan

## 📊 Project Status Overview

### What's Already Implemented ✅

1. **Guard class** (`guard.py`) - Main API with skeleton methods
   - `scan()` - Has basic placeholder logic
   - `detect_pii()` - Declared but needs implementation
   - `detect_prompt_injection()` - Declared but needs implementation

2. **GuardReport** (`core/report.py`) - Complete dataclass
   - Risk score validation (0.0-1.0)
   - Formatted `__str__()` output
   - All required fields

3. **PromptInjectionDetector** (`safety/injection_detector.py`) - Functional
   - Detects 3 basic phrases (case-insensitive)
   - `detect()` method fully working

4. **Project Structure** - Proper modular architecture established

---

## 🚀 Implementation Roadmap

### **PHASE 1: Core Safety Detectors**

#### **1. PIIDetector** (`guardllm/safety/pii_detector.py`)
**Priority:** 🔴 **HIGH**

Implement regex-based detection for:
- Email addresses
- Phone numbers (US/International formats)
- Credit card numbers (all major formats)
- Social Security Numbers (SSN)
- API keys and tokens
- IP addresses
- Passport numbers

**Method signature:**
```python
class PIIDetector:
    def detect(text: str) -> Dict[str, List[str]]
        """Returns detected types and their matches"""
    
    def has_pii(text: str) -> bool
        """Quick boolean check for presence of any PII"""
```

**Design considerations:**
- Use compiled regex patterns for performance
- Support configurable patterns
- Return detailed information about detected PII (type and partial value)
- Handle case-insensitive matching where appropriate

---

#### **2. RiskScorer Module** (`guardllm/safety/risk_scorer.py`)
**Priority:** 🔴 **HIGH**

Currently, scoring logic is hardcoded in `Guard.scan()`. Extract to separate module:
- Configurable risk weights per issue type
- Support for custom scoring rules
- Normalization to 0.0-1.0 range
- Cumulative scoring logic

**Method signature:**
```python
class RiskScorer:
    def score(issues: List[str], weights: Dict[str, float] = None) -> float
        """Calculate overall risk score from detected issues"""
    
    def add_custom_weight(issue_type: str, weight: float) -> None
        """Register custom scoring weights"""
    
    def get_weights() -> Dict[str, float]
        """Get current scoring weights"""
```

**Default Scoring Formula:**
```
- prompt_injection: +0.6
- pii_detected: +0.4
- (More patterns to be added as detectors expand)

Final Score = min(1.0, sum of all weights)
```

---

### **PHASE 2: Integration & Logging**

#### **3. AuditLogger** (`guardllm/observability/audit_logger.py`)
**Priority:** 🟡 **MEDIUM**

Implement structured logging for observability:
- Log scans with timestamp
- Track detection results
- Support file/console output
- Optional structured JSON format
- Thread-safe operations

**Method signature:**
```python
class AuditLogger:
    def log_scan(report: GuardReport, metadata: Dict = None) -> None
        """Log a complete scan with results"""
    
    def log_detection(detection_type: str, result: bool, details: Dict = None) -> None
        """Log individual detection event"""
    
    def export_logs(format: str = "json") -> str
        """Export audit trail in specified format"""
    
    def clear_logs() -> None
        """Clear stored logs"""
```

**Features:**
- Timestamp all log entries
- Support rotating file logs
- Optional console output
- JSON export capability
- Privacy-aware (can redact sensitive data)

---

#### **4. Improve PromptInjectionDetector** (`guardllm/safety/injection_detector.py`)
**Priority:** 🟡 **MEDIUM**

Expand detection patterns to include:
- "enter developer mode"
- "step-by-step instructions"
- "jailbreak" variants
- "pretend you are"
- "act as"
- "simulate"
- Multi-language support (basic)
- Pattern variations and typos

**Enhanced method signature:**
```python
class PromptInjectionDetector:
    def detect(text: str) -> bool
        """Updated with expanded patterns"""
    
    def detect_with_details(text: str) -> Dict[str, Any]
        """Returns which patterns matched and score"""
    
    def add_pattern(pattern: str) -> None
        """Allow runtime pattern addition"""
```

---

### **PHASE 3: Extended Features**

#### **5. Enhanced Guard Integration**
**Priority:** 🟡 **MEDIUM**

Update `guardllm/guard.py` to integrate all detectors:

**Enhanced method signatures:**
```python
class Guard:
    def __init__(self, config: GuardConfig = None) -> None
        """Initialize with optional configuration"""
    
    def detect_pii(text: str) -> Dict[str, List[str]]
        """Return detailed PII detection results"""
    
    def detect_prompt_injection(text: str) -> bool
        """Detect prompt injection attacks"""
    
    def scan(prompt: str, log: bool = True) -> GuardReport
        """Comprehensive scan with all detectors integrated"""
    
    def log_scan(report: GuardReport) -> None
        """Log scan results for observability"""
```

**Integration flow:**
1. PIIDetector runs first (fast regex-based)
2. PromptInjectionDetector runs second
3. RiskScorer calculates composite score
4. AuditLogger logs results (if enabled)
5. Return GuardReport with all findings

---

#### **6. Configuration System** (`guardllm/config.py`)
**Priority:** 🟡 **MEDIUM**

Create configuration class for Guard settings:

```python
@dataclass
class GuardConfig:
    """Configuration for Guard instance"""
    enable_pii_detection: bool = True
    enable_injection_detection: bool = True
    enable_audit_logging: bool = True
    custom_pii_patterns: Dict[str, str] = field(default_factory=dict)
    custom_scoring_weights: Dict[str, float] = field(default_factory=dict)
    log_file_path: Optional[str] = None
    redact_sensitive_data: bool = True
```

---

#### **7. Exception Handling** (`guardllm/exceptions.py`)
**Priority:** 🟡 **MEDIUM**

Define custom exceptions:

```python
class GuardLLMException(Exception):
    """Base exception for GuardLLM"""

class ConfigurationError(GuardLLMException):
    """Raised for configuration issues"""

class DetectionError(GuardLLMException):
    """Raised during detection process"""

class LoggingError(GuardLLMException):
    """Raised for logging failures"""
```

---

### **PHASE 4: Governance Module**

#### **8. Policy Manager** (`guardllm/governance/policy_manager.py`)
**Priority:** 🔵 **LOW**

Add policy enforcement layer:
- Define custom policies
- Enforce rules on scans
- Support blocking/warning modes

---

#### **9. Compliance Checker** (`guardllm/governance/compliance_checker.py`)
**Priority:** 🔵 **LOW**

Validate against compliance policies

---

### **PHASE 5: Quality Assurance**

#### **10. Comprehensive Test Suite**
**Priority:** 🔴 **HIGH**

Create tests in `tests/` directory:

- **`test_pii_detector.py`** - Test all PII patterns
- **`test_risk_scorer.py`** - Test scoring logic
- **`test_audit_logger.py`** - Test logging functionality
- **`test_guard_integration.py`** - Integration tests
- **`test_injection_detector_expanded.py`** - New pattern tests
- **`test_config.py`** - Configuration tests
- **`test_exceptions.py`** - Exception handling

**Test coverage target:** 90%+

---

#### **11. Documentation**
**Priority:** 🟡 **MEDIUM**

Expand documentation:
- Update `docs/getting_started.md` with new features
- Add API documentation for each module
- Add examples for each detector
- Create configuration guide
- Add troubleshooting section

---

#### **12. Production Readiness**
**Priority:** 🟡 **MEDIUM**

- Add type stub file (`py.typed`)
- Configure logging properly
- Add error handling for edge cases
- Performance optimization
- Add benchmarks

---

## 📋 Implementation Checklist

### Phase 1: Core Safety Detectors
- [ ] Create PIIDetector with regex patterns
- [ ] Create RiskScorer module
- [ ] Write tests for both modules
- [ ] Verify pattern accuracy

### Phase 2: Integration & Logging
- [ ] Create AuditLogger
- [ ] Expand PromptInjectionDetector
- [ ] Create Guard integration layer
- [ ] Write integration tests

### Phase 3: Extended Features
- [ ] Create GuardConfig
- [ ] Create exceptions module
- [ ] Update Guard class with new methods
- [ ] Add logging configuration

### Phase 4: Governance
- [ ] Create PolicyManager (optional first iteration)
- [ ] Create ComplianceChecker (optional first iteration)

### Phase 5: QA
- [ ] Write comprehensive tests
- [ ] Achieve 90%+ code coverage
- [ ] Update documentation
- [ ] Performance testing
- [ ] Review and refactor

---

## 📁 Files to Create

| File | Priority | Status | Phase |
|------|----------|--------|-------|
| `guardllm/safety/pii_detector.py` | 🔴 HIGH | Not Created | 1 |
| `guardllm/safety/risk_scorer.py` | 🔴 HIGH | Not Created | 1 |
| `guardllm/observability/audit_logger.py` | 🟡 MEDIUM | Not Created | 2 |
| `guardllm/config.py` | 🟡 MEDIUM | Not Created | 3 |
| `guardllm/exceptions.py` | 🟡 MEDIUM | Not Created | 3 |
| `guardllm/governance/policy_manager.py` | 🔵 LOW | Not Created | 4 |
| `guardllm/governance/compliance_checker.py` | 🔵 LOW | Not Created | 4 |
| `tests/test_pii_detector.py` | 🔴 HIGH | Not Created | 5 |
| `tests/test_risk_scorer.py` | 🔴 HIGH | Not Created | 5 |
| `tests/test_audit_logger.py` | 🟡 MEDIUM | Not Created | 5 |
| `tests/test_guard_integration.py` | 🟡 MEDIUM | Not Created | 5 |
| `tests/test_injection_detector_expanded.py` | 🟡 MEDIUM | Not Created | 5 |
| `tests/test_config.py` | 🟡 MEDIUM | Not Created | 5 |
| `tests/test_exceptions.py` | 🟡 MEDIUM | Not Created | 5 |

---

## 🎯 Recommended Implementation Order

```
Priority 1 (Must Have):
  1. PIIDetector (pii_detector.py)
  2. RiskScorer (risk_scorer.py)
  3. Test suite for detectors (test_pii_detector.py, test_risk_scorer.py)
  
Priority 2 (Core Integration):
  4. Update Guard class integration
  5. AuditLogger (audit_logger.py)
  6. GuardConfig (config.py)
  7. Exceptions (exceptions.py)
  8. Integration tests (test_guard_integration.py)
  
Priority 3 (Enhancement):
  9. Expand PromptInjectionDetector patterns
  10. Comprehensive test coverage
  11. Documentation improvements
  12. Performance optimization
  
Priority 4 (Optional):
  13. Governance module
  14. Advanced features
```

---

## 💡 Design Principles to Maintain

1. **Developer-first API design** - Keep interfaces simple and intuitive
2. **Modular architecture** - Each detector/logger independent
3. **Minimal dependencies** - Pure Python implementations preferred
4. **Extensibility** - Allow easy addition of new detectors/rules
5. **Type safety** - Full type hints throughout
6. **Production-ready** - Comprehensive error handling and logging
7. **Performance** - Efficient regex compilation and caching
8. **Testing** - High code coverage for reliability

---

## 📝 Notes

- All code should follow existing style guidelines (Black, Ruff)
- Include comprehensive docstrings for all public methods
- Add examples in docstrings where appropriate
- Maintain backward compatibility with existing Guard API
- Consider performance implications of pattern matching
- Thread-safety for observability module
- Support Python 3.9+ (as per pyproject.toml)

