from datetime import date
from pydantic import BaseModel


class WorkoutPlanRead(BaseModel):
    id: int
    client_id: int
    title: str

    class Config:
        from_attributes = True


class WorkoutPlanCreate(BaseModel):
    client_id: int
    title: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
