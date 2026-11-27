from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.order_status import OrderStatus


class OrderItemIn(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)


class OrderCreate(BaseModel):
    shipping_address: str = Field(min_length=10, max_length=500)
    items: list[OrderItemIn] = Field(min_length=1, max_length=20)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "shipping_address": "Demo Address, Pune, Maharashtra 411001",
                "items": [
                    {"product_id": 2, "quantity": 2},
                    {"product_id": 5, "quantity": 1},
                ],
            }
        }
    )


class OrderItemOut(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    line_total: float


class OrderOut(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: float
    shipping_address: str | None
    is_demo: bool
    created_at: datetime
    items: list[OrderItemOut]


class OrderSummary(BaseModel):
    id: int
    status: str
    total_amount: float
    item_count: int
    is_demo: bool
    created_at: datetime


class OrderListOut(BaseModel):
    items: list[OrderSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatusUpdate(BaseModel):
    status: OrderStatus

    # "CONFIRMED" & "confirmed" 
    @field_validator("status", mode="before")
    @classmethod
    def to_lower(cls, v):
        return v.lower() if isinstance(v, str) else v


class CancelRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class CancelOut(BaseModel):
    order_id: int
    result: str            # "cancelled"  "pending_approval"
    order_status: str
    message: str
    ticket_id: int | None = None