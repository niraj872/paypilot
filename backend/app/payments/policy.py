from dataclasses import dataclass

@dataclass
class PolicyDecision:
    allowed: bool
    reason: str
    requires_human: bool = False

class PaymentPolicyEngine:
    def evaluate(self, *, amount: float, max_budget: float, risk_score: int, risk_threshold: int, currency: str = "USD", allowed_currency: str = "USD", idempotent: bool = True) -> PolicyDecision:
        if currency != allowed_currency:
            return PolicyDecision(False, f"Currency {currency} is not allowed")
        if amount > max_budget:
            return PolicyDecision(False, f"Amount ${amount:.2f} exceeds user authorization ${max_budget:.2f}")
        if not idempotent:
            return PolicyDecision(False, "Duplicate transaction protection blocked this action")
        if risk_score >= risk_threshold:
            return PolicyDecision(False, f"Risk score {risk_score} exceeds threshold {risk_threshold}", True)
        return PolicyDecision(True, "Payment satisfies configured policy")
