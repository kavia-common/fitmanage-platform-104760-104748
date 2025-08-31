from pydantic import BaseModel, Field


class SubscriptionPlanRequest(BaseModel):
    """Request payload for subscription operations (checkout/activate)."""
    plan: str = Field(..., description="Plan identifier (e.g., basic, pro)")
