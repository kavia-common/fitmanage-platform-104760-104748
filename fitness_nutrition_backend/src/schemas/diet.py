from datetime import date
from pydantic import BaseModel


class DietPlanRead(BaseModel):
    id: int
    client_id: int
    title: str

    class Config:
        from_attributes = True


class DietPlanCreate(BaseModel):
    client_id: int
    title: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
