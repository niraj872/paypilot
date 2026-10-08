from app.payments.policy import PaymentPolicyEngine

def test_payment_within_budget_is_allowed():
    decision = PaymentPolicyEngine().evaluate(amount=95, max_budget=100, risk_score=8, risk_threshold=60)
    assert decision.allowed is True

def test_payment_above_budget_is_blocked():
    decision = PaymentPolicyEngine().evaluate(amount=150, max_budget=100, risk_score=8, risk_threshold=60)
    assert decision.allowed is False
    assert "exceeds" in decision.reason

def test_high_risk_requires_human():
    decision = PaymentPolicyEngine().evaluate(amount=95, max_budget=100, risk_score=85, risk_threshold=60)
    assert decision.allowed is False
    assert decision.requires_human is True

def test_wrong_currency_is_blocked():
    decision = PaymentPolicyEngine().evaluate(amount=95, max_budget=100, risk_score=8, risk_threshold=60, currency="EUR")
    assert decision.allowed is False
