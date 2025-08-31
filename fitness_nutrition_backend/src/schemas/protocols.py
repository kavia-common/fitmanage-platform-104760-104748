from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field


class ProtocolGoalRead(BaseModel):
    id: int
    client_id: int
    type: str
    title: str
    target_value: Decimal | None = None
    unit: str | None = None

    class Config:
        from_attributes = True


class ProtocolGoalCreate(BaseModel):
    client_id: int = Field(..., description="Target client id")
    type: str = Field(..., description="Goal type (e.g., weight, calories)")
    title: str
    target_value: Decimal | None = None
    unit: str | None = None
    notes: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class GoalProgressRead(BaseModel):
    id: int
    goal_id: int
    date: date
    value: Decimal
    notes: str | None = None

    class Config:
        from_attributes = True


class GoalProgressCreate(BaseModel):
    date: date
    value: Decimal
    notes: str | None = None
