from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user, require_roles, get_password_hash
from src.models import User, Role
from src.schemas.user import UserRead
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()


class UserUpdate(BaseModel):
    """Schema for updating user profile fields (self or by admin/pro)."""
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = Field(default=None, min_length=6)
    is_active: bool | None = None
    is_superuser: bool | None = None
    roles: list[str] | None = None  # role names to set (admin/pro only)

    class Config:
        extra = "forbid"


class AdminUserCreate(BaseModel):
    """Schema for admin/pro to create users with optional roles."""
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    roles: list[str] = Field(default_factory=list)


# PUBLIC_INTERFACE
@router.get("/", response_model=list[UserRead], summary="List users", dependencies=[Depends(require_roles("admin", "professional"))])
def list_users(db: Session = Depends(get_db)):
    """List users from the database. Requires admin or professional role."""
    return db.query(User).all()


# PUBLIC_INTERFACE
@router.get("/me", response_model=UserRead, summary="Get current user")
def get_me(current: User = Depends(get_current_user)):
    """Return the current authenticated user."""
    return current


# PUBLIC_INTERFACE
@router.get("/{user_id}", response_model=UserRead, summary="Get user by ID", dependencies=[Depends(require_roles("admin", "professional"))])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a single user by ID. Requires admin or professional."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# PUBLIC_INTERFACE
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Create user (admin/pro)", dependencies=[Depends(require_roles("admin", "professional"))])
def create_user(payload: AdminUserCreate, db: Session = Depends(get_db)):
    """Create a user with optional roles. Requires admin or professional."""
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        is_active=payload.is_active,
        is_superuser=payload.is_superuser,
        hashed_password=get_password_hash(payload.password),
    )

    # Ensure roles exist and assign
    if payload.roles:
        role_objs: list[Role] = []
        for name in payload.roles:
            role = db.query(Role).filter(Role.name == name).first()
            if not role:
                role = Role(name=name, description=f"Auto-created role {name}")
                db.add(role)
                db.flush()
            role_objs.append(role)
        user.roles = role_objs

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# PUBLIC_INTERFACE
@router.put("/{user_id}", response_model=UserRead, summary="Update user (self or admin/pro)")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Update a user. A user may update self (email/full_name/password). Admin/pro can update any user and roles/flags."""
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    current_roles = {r.name for r in (current.roles or [])}
    is_admin_or_pro = "admin" in current_roles or "professional" in current_roles
    is_self = current.id == target.id

    if not (is_self or is_admin_or_pro):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Self can change email/full_name/password. Admin/pro can change all including roles and flags.
    if payload.email is not None:
        if db.query(User).filter(User.email == payload.email, User.id != target.id).first():
            raise HTTPException(status_code=400, detail="Email already in use")
        target.email = payload.email
    if payload.full_name is not None:
        target.full_name = payload.full_name
    if payload.password:
        target.hashed_password = get_password_hash(payload.password)

    if is_admin_or_pro:
        if payload.is_active is not None:
            target.is_active = payload.is_active
        if payload.is_superuser is not None:
            target.is_superuser = payload.is_superuser
        if payload.roles is not None:
            role_objs: list[Role] = []
            for name in payload.roles:
                role = db.query(Role).filter(Role.name == name).first()
                if not role:
                    role = Role(name=name, description=f"Auto-created role {name}")
                    db.add(role)
                    db.flush()
                role_objs.append(role)
            target.roles = role_objs

    db.add(target)
    db.commit()
    db.refresh(target)
    return target


# PUBLIC_INTERFACE
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user (admin/pro)", dependencies=[Depends(require_roles("admin", "professional"))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user by ID. Requires admin or professional."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None
