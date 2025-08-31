from datetime import date
from pydantic import BaseModel


class SubscriptionRead(BaseModel):
    id: int
    user_id: int
    plan: str
    start_date: date
    end_date: date | None = None
    is_active: bool

    class Config:
        from_attributes = True
