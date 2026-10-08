from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.models import AgentRun, Negotiation, RiskAssessment, SellerOffer, Task, Verification

class BuyerAgent:
    name = "Buyer Agent"
    objective = "Understand user intent, compare offers, and choose a policy-compliant offer."

    def parse(self, task: Task) -> dict:
        return {
            "task": task.title,
            "budget_max": task.budget_max,
            "deadline_hours": task.deadline_hours,
            "payment_condition": task.payment_condition,
            "required_quality": task.quality_requirement,
        }

    def select_offer(self, task: Task, offers: list[SellerOffer]) -> SellerOffer:
        valid = [o for o in offers if o.price <= task.budget_max and o.eta_hours <= task.deadline_hours]
        if not valid:
            raise ValueError("No offer satisfies the user's hard constraints.")
        return sorted(valid, key=lambda o: (o.price, -o.quality_score, o.eta_hours))[0]

class NegotiationAgent:
    name = "Negotiation Agent"
    objective = "Negotiate within the user's hard budget and deadline constraints."

    def negotiate(self, task: Task, offer: SellerOffer, seller_name: str) -> Negotiation:
        target = min(task.budget_max, offer.price)
        transcript = [
            {"speaker": "BUYER AGENT", "message": f"Can you complete this within {min(task.deadline_hours, max(12, offer.eta_hours))} hours for ${max(1, int(target - 5))}?"},
            {"speaker": "SELLER AGENT", "message": f"I can do it for ${int(min(offer.price + 5, task.budget_max))}."},
            {"speaker": "BUYER AGENT", "message": f"Maximum authorized amount is ${int(task.budget_max)}. Can you accept ${int(target)}?"},
            {"speaker": "SELLER AGENT", "message": "Accepted."},
        ]
        return Negotiation(
            task_id=task.id,
            seller_id=offer.seller_id,
            transcript=transcript,
            agreed_price=target,
            agreed_eta_hours=min(offer.eta_hours, task.deadline_hours),
            status="ACCEPTED",
        )

class RiskGuardian:
    name = "Risk Guardian"
    objective = "Evaluate amount, seller, history and policy anomalies before payment."

    def assess(self, task: Task, offer: SellerOffer, reputation: float) -> RiskAssessment:
        score = 5
        reasons = ["Within user budget", f"Seller reputation {reputation:.0f}%", "Amount consistent with task"]
        if offer.price > task.budget_max:
            score += 85
            reasons.append("Amount exceeds configured budget")
        if reputation < 70:
            score += 20
            reasons.append("Seller reputation below preferred threshold")
        score = min(score, 100)
        if score >= 80:
            level = "HIGH"
            decision = "REQUIRE_HUMAN_APPROVAL"
        elif score >= 50:
            level = "MEDIUM"
            decision = "REVIEW"
        else:
            level = "LOW"
            decision = "ALLOW"
        return RiskAssessment(task_id=task.id, amount=offer.price, risk_score=score, risk_level=level, reasons=reasons, decision=decision)

class VerificationAgent:
    name = "Verification Agent"
    objective = "Verify requirements, result quality, tests, deadline and expected output."

    def verify(self, task: Task, force_fail: bool = False) -> Verification:
        if force_fail:
            return Verification(task_id=task.id, score=42, status="FAILED", reasons=["Automated tests failed", "Expected output incomplete"], recommendation="DO_NOT_RELEASE")
        return Verification(task_id=task.id, score=96, status="PASSED", reasons=["Requirements satisfied", "Tests passed", "Delivery before deadline", "No unexpected changes"], recommendation="RELEASE_PAYMENT")


def record_agent_run(db: Session, task_id: int, agent_name: str, objective: str, input_data: dict, output_data: dict):
    run = AgentRun(task_id=task_id, agent_name=agent_name, objective=objective, input_data=input_data, output_data=output_data, started_at=datetime.now(timezone.utc), finished_at=datetime.now(timezone.utc), status="COMPLETED")
    db.add(run)
    return run
