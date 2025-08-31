from datetime import date

from pydantic import BaseModel


class ClientRead(BaseModel):
    id: int
    display_name: str
    date_of_birth: date | None = None
    notes: str | None = None

    class Config:
        from_attributes = True


class ClientCreate(BaseModel):
    display_name: str
    date_of_birth: date | None = None
    notes: str | None = None
