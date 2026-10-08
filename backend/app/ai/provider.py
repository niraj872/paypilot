from typing import Any, Protocol

class AIProvider(Protocol):
    def generate(self, prompt: str, context: dict[str, Any] | None = None) -> str: ...
    def structured_output(self, prompt: str, schema: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]: ...
    def classify(self, text: str, labels: list[str]) -> str: ...
    def evaluate(self, criteria: dict[str, Any]) -> dict[str, Any]: ...

class DemoAIProvider:
    """Deterministic provider used for a reliable hackathon demo."""
    def generate(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        return "Deterministic demo response generated from structured task context."
    def structured_output(self, prompt: str, schema: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        return context or {}
    def classify(self, text: str, labels: list[str]) -> str:
        return labels[0] if labels else "UNKNOWN"
    def evaluate(self, criteria: dict[str, Any]) -> dict[str, Any]:
        return criteria
