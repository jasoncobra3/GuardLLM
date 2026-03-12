# GuardLLM

[![PyPI version](https://badge.fury.io/py/guardllm.svg)](https://badge.fury.io/py/guardllm)
[![Python versions](https://img.shields.io/pypi/pyversions/guardllm.svg)](https://pypi.org/project/guardllm/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Responsible AI toolkit for LLM applications providing **safety**, **governance**, and **observability** features.

## Overview

GuardLLM is a comprehensive library designed to help developers build safer, more transparent, and governed LLM applications. It provides production-ready tools for:

- **Prompt Injection Detection**: Identify and mitigate prompt injection attacks
- **PII Detection**: Detect and handle personally identifiable information
- **Audit Logging**: Comprehensive logging for governance and compliance
- **Safety Risk Scoring**: Quantify safety risks in LLM interactions

## Features

✨ **Out-of-the-box Safety Checks**: Pre-built detectors for common LLM vulnerabilities  
🔍 **Comprehensive Observability**: Track and log all LLM interactions  
📊 **Risk Scoring**: Quantify and monitor safety risks  
🛡️ **Governance Controls**: Enforce policies and compliance requirements  
🐍 **Easy Integration**: Simple, Pythonic API  
📦 **Production-Ready**: Type hints, comprehensive testing, and documentation  

## Installation

### From PyPI

```bash
pip install guardllm
```

### From Source

```bash
git clone https://github.com/GuardLLM/guardllm.git
cd guardllm
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/GuardLLM/guardllm.git
cd guardllm
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from guardllm import Guard

# Initialize the Guard
guard = Guard()

# Scan a prompt for safety issues
result = guard.scan("Your prompt here")

# Check the results
if result.is_safe:
    print("Prompt is safe to proceed")
else:
    print(f"Safety issues detected: {result.risks}")
```

### With Specific Detectors

```python
from guardllm import Guard

guard = Guard(
    enable_prompt_injection_detection=True,
    enable_pii_detection=True,
    enable_audit_logging=True,
)

result = guard.scan(
    prompt="User input here",
    context={"user_id": "user123", "session": "sess456"}
)

print(f"Risk Score: {result.risk_score}")
print(f"Detected Issues: {result.issues}")
```

See [examples/](examples/) for more usage patterns.

## Documentation

- [Getting Started Guide](docs/getting_started.md)
- [API Reference](https://guardllm.readthedocs.io/api/)
- [Examples](examples/)

## Architecture

```
guardllm/
├── safety/           # Safety detection modules
├── governance/       # Governance and policy modules
├── observability/    # Logging and monitoring modules
├── utils/           # Utility functions and helpers
└── guard.py         # Main Guard class
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://guardllm.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/GuardLLM/guardllm/issues)
- 💬 [Discussions](https://github.com/GuardLLM/guardllm/discussions)

## Citation

If you use GuardLLM in your research, please cite:

```bibtex
@software{guardllm2024,
  title={GuardLLM: A Responsible AI Toolkit for LLM Applications},
  author={GuardLLM Contributors},
  year={2024},
  url={https://github.com/GuardLLM/guardllm}
}
```

## Roadmap

- [ ] Enhanced prompt injection detection models
- [ ] Multi-language PII detection
- [ ] Advanced risk scoring algorithms
- [ ] Integration with major LLM platforms
- [ ] Web dashboard for monitoring
- [ ] Real-time alerting system

## Acknowledgments

GuardLLM is built with best practices from the responsible AI and security communities.
