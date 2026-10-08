from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    max_budget: Mapped[float] = mapped_column(Float, default=100.0)
    risk_threshold: Mapped[int] = mapped_column(Integer, default=60)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

class Seller(Base):
    __tablename__ = "sellers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    capability: Mapped[str] = mapped_column(String(255))
    base_price: Mapped[float] = mapped_column(Float)
    eta_hours: Mapped[int] = mapped_column(Integer)
    quality_score: Mapped[float] = mapped_column(Float)
    reputation: Mapped[float] = mapped_column(Float)
    availability: Mapped[bool] = mapped_column(Boolean, default=True)
    negotiation_policy: Mapped[dict] = mapped_column(JSON, default=dict)
    offers = relationship("SellerOffer", back_populates="seller")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    budget_max: Mapped[float] = mapped_column(Float)
    deadline_hours: Mapped[int] = mapped_column(Integer)
    payment_condition: Mapped[str] = mapped_column(String(80), default="release_after_verification")
    quality_requirement: Mapped[str] = mapped_column(String(255), default="tests_pass")
    status: Mapped[str] = mapped_column(String(64), default="REQUEST_CREATED")
    demo_mode: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    user = relationship("User", back_populates="tasks")
    offers = relationship("SellerOffer", back_populates="task", cascade="all, delete-orphan")
    negotiations = relationship("Negotiation", back_populates="task", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="task", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="task", cascade="all, delete-orphan")
    verification = relationship("Verification", back_populates="task", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="task", cascade="all, delete-orphan")

class SellerOffer(Base):
    __tablename__ = "seller_offers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"))
    price: Mapped[float] = mapped_column(Float)
    eta_hours: Mapped[int] = mapped_column(Integer)
    quality_score: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(64), default="OFFERED")
    task = relationship("Task", back_populates="offers")
    seller = relationship("Seller", back_populates="offers")

class Negotiation(Base):
    __tablename__ = "negotiations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"))
    transcript: Mapped[list] = mapped_column(JSON, default=list)
    agreed_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    agreed_eta_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="NEGOTIATING")
    task = relationship("Task", back_populates="negotiations")

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    agent_name: Mapped[str] = mapped_column(String(120))
    objective: Mapped[str] = mapped_column(Text)
    input_data: Mapped[dict] = mapped_column(JSON, default=dict)
    output_data: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(64), default="COMPLETED")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    amount: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(16))
    reasons: Mapped[list] = mapped_column(JSON, default=list)
    decision: Mapped[str] = mapped_column(String(64))
    task = relationship("Task", back_populates="risk_assessments")

class PaymentPolicy(Base):
    __tablename__ = "payment_policies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    max_transaction_amount: Mapped[float] = mapped_column(Float)
    approval_threshold: Mapped[float] = mapped_column(Float, default=100.0)
    risk_threshold: Mapped[int] = mapped_column(Integer, default=60)
    allowed_currency: Mapped[str] = mapped_column(String(3), default="USD")
    require_verification: Mapped[bool] = mapped_column(Boolean, default=True)
    require_approval_above_threshold: Mapped[bool] = mapped_column(Boolean, default=True)

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    provider: Mapped[str] = mapped_column(String(32), default="PAYPAL")
    provider_order_id: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    authorization_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="PENDING")
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)
    approval_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    task = relationship("Task", back_populates="payments")

class Verification(Base):
    __tablename__ = "verifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), unique=True)
    score: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(64))
    reasons: Mapped[list] = mapped_column(JSON, default=list)
    recommendation: Mapped[str] = mapped_column(String(64))
    task = relationship("Task", back_populates="verification")

class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_event_id: Mapped[str] = mapped_column(String(160), unique=True)
    event_type: Mapped[str] = mapped_column(String(160))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"))
    paypal_order_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    verification_score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(64), default="AUTHORIZED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    actor: Mapped[str] = mapped_column(String(120))
    action: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(64))
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    task = relationship("Task", back_populates="audit_logs")
