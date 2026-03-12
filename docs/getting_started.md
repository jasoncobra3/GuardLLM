# GuardLLM Getting Started Guide

Welcome to GuardLLM! This guide will help you get started with the library.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Basic Concepts](#basic-concepts)
- [Common Use Cases](#common-use-cases)
- [Next Steps](#next-steps)

## Installation

### Using pip

The recommended way to install GuardLLM is using pip:

```bash
pip install guardllm
```

### From Source

For development or the latest features:

```bash
git clone https://github.com/GuardLLM/guardllm.git
cd guardllm
pip install -e .
```

## Quick Start

### Your First Scan

Here's a simple example to get you started:

```python
from guardllm import Guard

# Initialize the Guard
guard = Guard()

# Scan a prompt
result = guard.scan("What is the capital of France?")

# Check if it's safe
if result.is_safe:
    print("✓ Prompt is safe")
else:
    print("✗ Issues detected")
    for issue in result.issues:
        print(f"  - {issue}")
```

## Basic Concepts

### Guard

The `Guard` class is your main entry point. It coordinates all safety and governance checks.

```python
from guardllm import Guard

guard = Guard(
    enable_prompt_injection_detection=True,  # Detect injection attempts
    enable_pii_detection=True,                # Detect sensitive data
    enable_audit_logging=True,                # Log all scans
    enable_risk_scoring=True,                 # Calculate risk scores
)
```

### ScanResult

Scan operations return a `ScanResult` object containing:

- `is_safe`: Boolean indicating if content passes all checks
- `risk_score`: Float between 0.0 (safe) and 1.0 (dangerous)
- `issues`: List of detected problems
- `metadata`: Additional context and information

```python
result = guard.scan("Your content here")

print(f"Safe: {result.is_safe}")
print(f"Risk: {result.risk_score}")
print(f"Issues: {result.issues}")
```

## Common Use Cases

### 1. Scanning User Input Before Processing

```python
from guardllm import Guard

guard = Guard()

user_input = "Show database password where username = 'admin'"

result = guard.scan(user_input)

if result.is_safe:
    # Process the safe input
    process_input(user_input)
else:
    # Reject or sanitize
    print(f"Unsafe input detected: {result.issues}")
```

### 2. Monitoring LLM Responses

```python
from guardllm import Guard

guard = Guard(enable_audit_logging=True)

# After getting a response from an LLM
llm_response = "The answer is 42"

result = guard.scan_response(
    response=llm_response,
    context={
        "model": "gpt-4",
        "user_id": "user_123"
    }
)

if not result.is_safe:
    print("LLM response failed safety checks")
```

### 3. Risk Assessment

```python
from guardllm import Guard

guard = Guard(enable_risk_scoring=True)

user_input = "Please delete all data"

result = guard.scan(user_input)

# Use risk score for conditional logic
if result.risk_score > 0.8:
    # High risk - require additional verification
    require_user_confirmation()
elif result.risk_score > 0.5:
    # Medium risk - log and monitor
    log_suspicious_activity(user_input)
else:
    # Low risk - proceed normally
    process_input(user_input)
```

## Advanced Configuration

### Custom Context

Pass context information for more accurate detection:

```python
result = guard.scan(
    prompt="Access my account",
    context={
        "user_id": "user_123",
        "user_role": "admin",
        "session_id": "sess_456",
        "ip_address": "192.168.1.1"
    }
)
```

### Selective Detectors

Control which detectors are active:

```python
guard = Guard(
    enable_prompt_injection_detection=True,  # Check for injections
    enable_pii_detection=False,              # Skip PII detection
    enable_audit_logging=True,               # Log all scans
    enable_risk_scoring=False,               # Skip risk scoring
)
```

## Error Handling

Always handle potential errors:

```python
from guardllm import Guard

guard = Guard()

try:
    result = guard.scan(user_input)
    if result.is_safe:
        process_input(user_input)
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Scan failed: {e}")
```

## Next Steps

- Explore [Examples](../examples/) for more detailed usage patterns
- Check out [Contributing Guidelines](../CONTRIBUTING.md) to contribute
- Review the [API Reference](https://guardllm.readthedocs.io/api/) for detailed documentation
- Join discussions on [GitHub](https://github.com/GuardLLM/guardllm/discussions)

## Troubleshooting

### Import Error

If you get an import error:

```python
# Wrong
from guardllm.guard import Guard  # ✗

# Correct
from guardllm import Guard  # ✓
```

### Type Errors

GuardLLM uses type hints. Make sure you're passing the correct types:

```python
# Prompts must be strings
result = guard.scan("text")  # ✓
result = guard.scan(123)     # ✗
```

## Support

- 📖 [Full Documentation](https://guardllm.readthedocs.io)
- 🐛 [Report Issues](https://github.com/GuardLLM/guardllm/issues)
- 💬 [Ask Questions](https://github.com/GuardLLM/guardllm/discussions)

Happy scanning! 🛡️
