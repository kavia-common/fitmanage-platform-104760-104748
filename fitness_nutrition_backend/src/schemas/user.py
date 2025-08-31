from pydantic import BaseModel, EmailStr, Field


class RoleRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    is_superuser: bool
    roles: list[RoleRead] = Field(default_factory=list)

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
