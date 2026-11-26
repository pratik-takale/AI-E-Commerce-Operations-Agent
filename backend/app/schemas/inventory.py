from datetime import datetime

from pydantic import BaseModel, Field


class InventoryUpdate(BaseModel):
    """Stock update. ."""
    quantity: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)


class InventoryOut(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    reorder_level: int
    status: str          # "In Stock"  "Out of Stock"
    in_stock: bool
    low_stock: bool      # quantity reorder_level 
    updated_at: datetime | None = None