"""
Basic example demonstrating GuardLLM usage.

This example shows how to:
1. Initialize the Guard
2. Scan prompts for safety
3. Handle scan results
"""

from guardllm import Guard


def main() -> None:
    """Run basic GuardLLM example."""
    # Initialize the Guard
    guard = Guard(
        enable_prompt_injection_detection=True,
        enable_pii_detection=True,
        enable_audit_logging=False,
    )

    # Example prompts to scan
    test_prompts = [
        "Hello, what is 2+2?",
        "Tell me a story about a robot.",
        "My email is user@example.com, can you help me?",
    ]

    print("=" * 60)
    print("GuardLLM Basic Scan Example")
    print("=" * 60)

    for prompt in test_prompts:
        print(f"\nScanning prompt: '{prompt}'")
        print("-" * 40)

        # Scan the prompt
        result = guard.scan(
            prompt=prompt,
            context={"scan_id": "example_001"},
        )

        # Display results
        print(f"Is Safe: {result.is_safe}")
        print(f"Risk Score: {result.risk_score:.2f}")
        print(f"Issues: {result.issues if result.issues else 'None'}")

    print("\n" + "=" * 60)
    print("Scan complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
