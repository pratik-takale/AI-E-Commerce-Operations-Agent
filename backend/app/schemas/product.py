from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    """नवा product बनवताना येणारा data"""
    name: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=5)
    price: float = Field(ge=0, description="किंमत ₹ मध्ये, ऋण असू शकत नाही")
    category: str = Field(min_length=2, max_length=100)
    initial_stock: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "OnePlus Phone (Test)",
                "description": "Sample product used for API testing.",
                "price": 29999,
                "category": "Smartphones",
                "initial_stock": 20,
                "reorder_level": 5,
            }
        }
    )


class ProductUpdate(BaseModel):
    """Update करताना फक्त बदलायचे fields पाठवा, बाकी तसेच राहतात"""
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, min_length=5)
    price: float | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, min_length=2, max_length=100)


class ProductOut(BaseModel):
    """Client ला परत जाणारा product"""
    id: int
    name: str
    description: str
    price: float
    category: str
    is_active: bool
    is_demo: bool
    quantity: int
    stock_status: str


class ProductListOut(BaseModel):
    """Pagination सह यादी"""
    items: list[ProductOut]
    total: int
    page: int
    page_size: int
    total_pages: int