from sqlalchemy import select
from app.db.models import PaymentPolicy, Seller, SellerOffer, User, Task

def seed(db):
    user = db.scalar(select(User).where(User.email == "demo@paypilot.local"))
    if not user:
        user = User(name="Demo User", email="demo@paypilot.local", max_budget=100, risk_threshold=60)
        db.add(user)
        db.flush()
    if not db.scalar(select(PaymentPolicy).where(PaymentPolicy.user_id == user.id)):
        db.add(PaymentPolicy(user_id=user.id, max_transaction_amount=100, approval_threshold=100, risk_threshold=60, allowed_currency="USD", require_verification=True))
    sellers = [
        ("CodeForge", "React/Python engineering", 85, 18, 88, 94),
        ("RapidStack", "Frontend debugging and delivery", 120, 8, 96, 91),
        ("DevNova", "React + test automation", 100, 12, 92, 96),
    ]
    existing = {s.name for s in db.scalars(select(Seller)).all()}
    for name, cap, price, eta, quality, rep in sellers:
        if name not in existing:
            db.add(Seller(name=name, capability=cap, base_price=price, eta_hours=eta, quality_score=quality, reputation=rep, availability=True, negotiation_policy={"max_discount": 5}))
    db.commit()
