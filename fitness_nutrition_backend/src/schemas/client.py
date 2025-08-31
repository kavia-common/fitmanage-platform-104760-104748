from datetime import date

from pydantic import BaseModel, Field


class ClientRead(BaseModel):
    id: int
    display_name: str
    date_of_birth: date | None = None
    notes: str | None = None

    class Config:
        from_attributes = True


class ClientCreate(BaseModel):
    display_name: str = Field(..., description="Client display name")
    date_of_birth: date | None = Field(default=None, description="DOB")
    notes: str | None = Field(default=None, description="Notes/medical info")
    # Only honored for admin/pro creators; regular users will be forced to their own id
    user_id: int | None = Field(default=None, description="User owner id (admin/pro only)")
