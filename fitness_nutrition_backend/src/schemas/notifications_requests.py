from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    """Request payload to create a notification for the current user."""
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification body text")
    # In this iteration, user_id is intentionally not exposed to prevent cross-user creation.
