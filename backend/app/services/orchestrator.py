from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.agents.agents import BuyerAgent, NegotiationAgent, RiskGuardian, VerificationAgent, record_agent_run
from app.db.models import AuditLog, Payment, PaymentPolicy, SellerOffer, Task, Transaction, User
from app.payments.policy import PaymentPolicyEngine

class Orchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.buyer = BuyerAgent()
        self.negotiation = NegotiationAgent()
        self.risk = RiskGuardian()
        self.verification = VerificationAgent()
        self.policy = PaymentPolicyEngine()

    def audit(self, task_id: int, actor: str, action: str, status: str, metadata: dict):
        self.db.add(AuditLog(task_id=task_id, actor=actor, action=action, status=status, meta=metadata))

    def run(self, task, force_fail_verification: bool = False, force_budget_failure: bool = False):
        user = self.db.get(User, task.user_id)
        task.status = "OFFERS_FOUND"
        parsed = self.buyer.parse(task)
        record_agent_run(self.db, task.id, self.buyer.name, self.buyer.objective, {"description": task.description}, parsed)
        self.audit(task.id, "Buyer Agent", "TASK_PARSED", "COMPLETED", parsed)

        offers = list(self.db.scalars(select(SellerOffer).where(SellerOffer.task_id == task.id)).all())
        if force_budget_failure:
            offer = max(offers, key=lambda x: x.price)
        else:
            offer = self.buyer.select_offer(task, offers)
        seller = offer.seller
        task.status = "NEGOTIATING"
        negotiation = self.negotiation.negotiate(task, offer, seller.name)
        self.db.add(negotiation)
        self.db.flush()
        record_agent_run(self.db, task.id, self.negotiation.name, self.negotiation.objective, {"offer_id": offer.id}, {"agreed_price": negotiation.agreed_price})
        self.audit(task.id, "Negotiation Agent", "NEGOTIATION_ACCEPTED", "COMPLETED", {"seller": seller.name, "price": negotiation.agreed_price})

        selected_price = float(negotiation.agreed_price or offer.price)
        if force_budget_failure:
            selected_price = max(selected_price, task.budget_max + 50)
        risk = self.risk.assess(task, offer, seller.reputation)
        risk.amount = selected_price
        if selected_price > task.budget_max:
            risk.risk_score = 87
            risk.risk_level = "HIGH"
            risk.decision = "BLOCK"
            risk.reasons.append("Negotiated amount exceeds configured budget")
        self.db.add(risk)
        self.db.flush()
        record_agent_run(self.db, task.id, self.risk.name, self.risk.objective, {"amount": selected_price}, {"risk_score": risk.risk_score, "risk_level": risk.risk_level})
        self.audit(task.id, "Risk Guardian", "RISK_ASSESSED", risk.decision, {"score": risk.risk_score, "reasons": risk.reasons})

        policy = self.db.scalar(select(PaymentPolicy).where(PaymentPolicy.user_id == user.id))
        decision = self.policy.evaluate(amount=selected_price, max_budget=task.budget_max, risk_score=risk.risk_score, risk_threshold=policy.risk_threshold)
        if not decision.allowed:
            task.status = "PAYMENT_BLOCKED" if not decision.requires_human else "HUMAN_APPROVAL_REQUIRED"
            self.audit(task.id, "Policy Engine", "PAYMENT_POLICY", "BLOCKED", {"reason": decision.reason})
            self.db.commit()
            return {"task": task, "offer": offer, "risk": risk, "payment": None, "verification": None, "policy": decision}

        task.status = "PAYMENT_PENDING"
        payment = Payment(task_id=task.id, amount=selected_price, currency="USD", provider="PAYPAL", status="PENDING", idempotency_key=f"task-{task.id}-payment")
        self.db.add(payment)
        self.db.flush()
        self.audit(task.id, "Policy Engine", "PAYMENT_POLICY_ALLOWED", "ALLOWED", {"amount": selected_price})
        task.status = "PAYMENT_AUTHORIZED"
        payment.status = "AUTHORIZED"
        verification = self.verification.verify(task, force_fail=force_fail_verification)
        self.db.add(verification)
        self.db.flush()
        record_agent_run(self.db, task.id, self.verification.name, self.verification.objective, {"task": task.title}, {"score": verification.score, "status": verification.status})
        self.audit(task.id, "Verification Agent", "VERIFICATION_COMPLETED", verification.status, {"score": verification.score})
        if verification.status == "PASSED":
            task.status = "PAYMENT_COMPLETED"
            payment.status = "COMPLETED"
            self.db.add(Transaction(payment_id=payment.id, paypal_order_id=payment.provider_order_id, amount=payment.amount, risk_score=risk.risk_score, verification_score=verification.score, status="COMPLETED"))
            self.audit(task.id, "Orchestrator", "PAYMENT_COMPLETED", "COMPLETED", {"amount": payment.amount})
        else:
            task.status = "VERIFICATION_FAILED"
            payment.status = "NOT_RELEASED"
            self.audit(task.id, "Orchestrator", "PAYMENT_NOT_RELEASED", "BLOCKED", {"reason": "Verification failed"})
        self.db.commit()
        return {"task": task, "offer": offer, "risk": risk, "payment": payment, "verification": verification, "policy": decision}
