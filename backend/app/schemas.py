from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10)
    budget_max: float = Field(gt=0, le=100000)
    deadline_hours: int = Field(gt=0, le=720)
    payment_condition: str = "release_after_verification"
    quality_requirement: str = "tests_pass"

class TaskRunResponse(BaseModel):
    task_id: int
    status: str
    selected_offer_id: int | None = None
    selected_seller: str | None = None
    negotiated_price: float | None = None
    risk_score: int | None = None
    risk_level: str | None = None
    payment_status: str | None = None
    verification_score: float | None = None
    verification_status: str | None = None
    message: str

class PaymentCreateRequest(BaseModel):
    task_id: int

class PaymentCaptureRequest(BaseModel):
    task_id: int

class AnalyticsQuery(BaseModel):
    query: str = Field(min_length=3, max_length=500)

class FailureScenarioRequest(BaseModel):
    scenario: str = Field(pattern="^(budget_exceeded|verification_failed)$")
